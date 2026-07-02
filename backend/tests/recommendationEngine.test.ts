import { generateTargetRecommendation } from '../src/services/recommendationEngine';
import { RoadmapProgress } from '@prisma/client';
import { CFProblem } from '../src/services/codeforces';
import { RoadmapTopic } from '../src/config/roadmap';

describe('RecommendationEngine', () => {
  const dummyProgress: RoadmapProgress[] = [
    {
      id: '1',
      userId: 'user1',
      topic: 'Hashing',
      attemptedCount: 10,
      solvedCount: 9,
      targetRating: 1200,
      updatedAt: new Date()
    },
    {
      id: '2',
      userId: 'user1',
      topic: 'Dynamic Programming',
      attemptedCount: 10, // 0% solve rate, highly weak
      solvedCount: 0,
      targetRating: 1500,
      updatedAt: new Date()
    }
  ];

  const dummyProblems: CFProblem[] = [
    { contestId: 1, index: 'A', name: 'Hash Prob', tags: ['hashing'], rating: 1200 },
    { contestId: 2, index: 'A', name: 'DP Prob 1', tags: ['dp'], rating: 1500 }, // Perfect match
    { contestId: 2, index: 'B', name: 'DP Prob 2', tags: ['dp'], rating: 1500 }, // Solved match
    { contestId: 3, index: 'A', name: 'Hard DP', tags: ['dp'], rating: 3000 },
  ];

  const mockLLM = async (topic: string, target: number, name: string) => `LLM Rationale for ${name}`;

  it('selects an unsolved problem from the weakest topic within the target rating band', async () => {
    const solvedIds = new Set(['2B']); // User already solved DP Prob 2
    
    const rec = await generateTargetRecommendation(
      dummyProgress,
      dummyProblems,
      solvedIds,
      mockLLM
    );

    // It should pick 'Dynamic Programming' because it has the highest weakness score.
    // It should NOT pick 2B because it's in solvedIds.
    // It should pick 2A because it exactly matches the target rating of 1500.
    
    expect(rec).not.toBeNull();
    expect(rec?.topic).toBe('Dynamic Programming');
    expect(rec?.problemId).toBe('2A');
    expect(rec?.title).toBe('DP Prob 1');
    expect(rec?.rationale).toBe('LLM Rationale for DP Prob 1');
  });

  it('falls back to widening the rating band if exact rating is not found', async () => {
    // Modify target rating so no exact match exists.
    const progressModified = [...dummyProgress];
    progressModified[1].targetRating = 1700; // DP target is 1700. Only 1500 and 3000 exist.
    
    const solvedIds = new Set<string>(); // none solved
    
    const rec = await generateTargetRecommendation(
      progressModified,
      dummyProblems,
      solvedIds,
      mockLLM
    );

    // It searches bands [1700, 1700], then [1600, 1800], then [1500, 1900].
    // At +/- 200, it finds DP Prob 1 (1500) and DP Prob 2 (1500).
    expect(rec).not.toBeNull();
    expect(rec?.rating).toBe(1500);
  });
});
