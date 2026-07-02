import { RoadmapProgress } from '@prisma/client';
import { CFProblem } from './codeforces';
import { topicToTags, RoadmapTopic } from '../config/roadmap';
import { getRatingBands } from './rating';
import { calculateWeaknessScore } from './weakness';

export interface RecommendationResult {
  title: string;
  url: string;
  rating?: number;
  tags: string[];
  topic: string;
  rationale: string;
  problemId: string;
}

export async function generateTargetRecommendation(
  progress: RoadmapProgress[],
  allProblems: CFProblem[],
  solvedProblemIds: Set<string>,
  generateRationale: (topic: string, targetRating: number, problemName: string, problemRating?: number) => Promise<string>
): Promise<RecommendationResult | null> {
  if (progress.length === 0) {
    return null;
  }

  // 1. Calculate Weakness Scores and find the weakest topic
  const progressWithWeakness = progress.map(p => ({
    ...p,
    weaknessScore: calculateWeaknessScore(p.attemptedCount, p.solvedCount)
  }));

  progressWithWeakness.sort((a, b) => b.weaknessScore - a.weaknessScore);
  const weakestTopic = progressWithWeakness[0];

  // 2. Filter Candidate Problems
  const topicTags = topicToTags[weakestTopic.topic as RoadmapTopic];
  if (!topicTags) return null;

  const candidateProblems = allProblems.filter(p => {
    const probId = `${p.contestId}${p.index}`;
    if (solvedProblemIds.has(probId)) return false;
    return p.tags && p.tags.some(tag => topicTags.includes(tag));
  });

  // 3. Find a problem within the rating bands
  const bands = getRatingBands(weakestTopic.targetRating);
  let selectedProblem = null;

  for (const band of bands) {
    const matched = candidateProblems.filter(p => 
      p.rating !== undefined && p.rating >= band.min && p.rating <= band.max
    );
    if (matched.length > 0) {
      selectedProblem = matched[Math.floor(Math.random() * matched.length)];
      break;
    }
  }

  // Fallback: If no problem matches the rating bands, just pick a random unsolved problem for this topic
  if (!selectedProblem && candidateProblems.length > 0) {
    selectedProblem = candidateProblems[Math.floor(Math.random() * candidateProblems.length)];
  }

  if (!selectedProblem) {
    return null; // No recommended problems found for this topic at all
  }

  // 4. Generate LLM Rationale
  const rationale = await generateRationale(
    weakestTopic.topic,
    weakestTopic.targetRating,
    selectedProblem.name,
    selectedProblem.rating
  );

  return {
    title: selectedProblem.name,
    url: `https://codeforces.com/contest/${selectedProblem.contestId}/problem/${selectedProblem.index}`,
    rating: selectedProblem.rating,
    tags: selectedProblem.tags,
    topic: weakestTopic.topic,
    rationale,
    problemId: `${selectedProblem.contestId}${selectedProblem.index}`
  };
}
