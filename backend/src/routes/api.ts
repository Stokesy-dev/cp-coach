import { Router, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { AuthRequest, requireAuth } from '../middleware/auth';
import { fetchUserSubmissions, fetchAllProblems } from '../services/codeforces';
import { roadmapTopics, topicToTags, RoadmapTopic } from '../config/roadmap';
import { calculateInitialTargetRating, adjustTargetRating, getRatingBands } from '../services/rating';
import { calculateWeaknessScore } from '../services/weakness';
import { generateRecommendationRationale } from '../services/llm';
import { generateTargetRecommendation } from '../services/recommendationEngine';

const router = Router();
const prisma = new PrismaClient();

router.use(requireAuth);

router.get('/me', async (req: AuthRequest, res: Response, next) => {
  try {
    const user = await prisma.user.findUnique({ where: { id: req.user!.id } });
    res.json(user);
  } catch (error) {
    next(error);
  }
});

router.post('/handle', async (req: AuthRequest, res: Response, next) => {
  try {
    const { codeforcesHandle } = req.body;
    if (!codeforcesHandle) {
      res.status(400).json({ error: 'codeforcesHandle is required' });
      return;
    }

    const submissions = await fetchUserSubmissions(codeforcesHandle);

    await prisma.user.update({
      where: { id: req.user!.id },
      data: { codeforcesHandle }
    });

    const allSolvedRatings: number[] = [];
    const tagSolvedRatings: Record<string, number[]> = {};
    const tagStats: Record<string, { attempted: Set<string>; solved: Set<string> }> = {};

    roadmapTopics.forEach(topic => {
      tagSolvedRatings[topic] = [];
      tagStats[topic] = { attempted: new Set(), solved: new Set() };
    });

    submissions.forEach(sub => {
      const probId = `${sub.problem.contestId}${sub.problem.index}`;
      const isSolved = sub.verdict === 'OK';
      if (isSolved && sub.problem.rating) {
        allSolvedRatings.push(sub.problem.rating);
      }

      roadmapTopics.forEach(topic => {
        const topicTags = topicToTags[topic as RoadmapTopic];
        if (sub.problem.tags && sub.problem.tags.some(tag => topicTags.includes(tag))) {
          tagStats[topic].attempted.add(probId);
          if (isSolved) {
            tagStats[topic].solved.add(probId);
            if (sub.problem.rating) {
              tagSolvedRatings[topic].push(sub.problem.rating);
            }
          }
        }
      });
    });

    for (const topic of roadmapTopics) {
      const stats = tagStats[topic];
      const attemptedCount = stats.attempted.size;
      const solvedCount = stats.solved.size;

      const existing = await prisma.roadmapProgress.findUnique({
        where: { userId_topic: { userId: req.user!.id, topic } }
      });

      if (existing) {
        await prisma.roadmapProgress.update({
          where: { id: existing.id },
          data: { attemptedCount, solvedCount }
        });
      } else {
        const initialRating = calculateInitialTargetRating(tagSolvedRatings[topic], allSolvedRatings);
        await prisma.roadmapProgress.create({
          data: {
            userId: req.user!.id,
            topic,
            attemptedCount,
            solvedCount,
            targetRating: initialRating
          }
        });
      }
    }

    res.json({ message: 'Handle linked and progress initialized/synced' });
  } catch (error) {
    next(error);
  }
});

router.get('/roadmap', async (req: AuthRequest, res: Response, next) => {
  try {
    const progress = await prisma.roadmapProgress.findMany({
      where: { userId: req.user!.id }
    });

    const progressWithWeakness = progress.map(p => ({
      ...p,
      weaknessScore: calculateWeaknessScore(p.attemptedCount, p.solvedCount)
    }));

    progressWithWeakness.sort((a, b) => b.weaknessScore - a.weaknessScore);

    res.json(progressWithWeakness);
  } catch (error) {
    next(error);
  }
});

router.post('/recommend', async (req: AuthRequest, res: Response, next) => {
  try {
    const user = await prisma.user.findUnique({ where: { id: req.user!.id } });
    if (!user || !user.codeforcesHandle) {
      res.status(400).json({ error: 'Please link a Codeforces handle first' });
      return;
    }

    const progress = await prisma.roadmapProgress.findMany({
      where: { userId: req.user!.id }
    });

    if (progress.length === 0) {
      res.status(400).json({ error: 'Roadmap progress not initialized' });
      return;
    }

    // Fetch all external data
    const problems = await fetchAllProblems();
    const submissions = await fetchUserSubmissions(user.codeforcesHandle);
    
    // Compute solved problem IDs
    const solvedProbIds = new Set(
      submissions.filter(s => s.verdict === 'OK').map(s => `${s.problem.contestId}${s.problem.index}`)
    );

    // Call the pure Recommendation Engine
    const recommendation = await generateTargetRecommendation(
      progress,
      problems,
      solvedProbIds,
      generateRecommendationRationale
    );

    if (!recommendation) {
      res.status(404).json({ error: 'No recommended problems found for this topic' });
      return;
    }

    res.json(recommendation);

  } catch (error) {
    next(error);
  }
});

router.post('/feedback', async (req: AuthRequest, res: Response, next) => {
  try {
    const { topic, result, problemId } = req.body;
    if (!topic || !result || !['pass', 'fail'].includes(result)) {
      res.status(400).json({ error: 'Invalid input' });
      return;
    }

    const progress = await prisma.roadmapProgress.findUnique({
      where: { userId_topic: { userId: req.user!.id, topic } }
    });

    if (!progress) {
      res.status(404).json({ error: 'Topic progress not found' });
      return;
    }

    const newTargetRating = adjustTargetRating(progress.targetRating, result);
    const newAttemptedCount = progress.attemptedCount + 1;
    const newSolvedCount = progress.solvedCount + (result === 'pass' ? 1 : 0);

    await prisma.roadmapProgress.update({
      where: { id: progress.id },
      data: {
        targetRating: newTargetRating,
        attemptedCount: newAttemptedCount,
        solvedCount: newSolvedCount
      }
    });

    res.json({ message: 'Feedback recorded', newTargetRating });
  } catch (error) {
    next(error);
  }
});

export default router;
