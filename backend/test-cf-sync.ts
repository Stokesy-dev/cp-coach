import { fetchUserSubmissions } from './src/services/codeforces';
import { roadmapTopics, topicToTags, RoadmapTopic } from './src/config/roadmap';

async function run() {
  const submissions = await fetchUserSubmissions('tourist'); // use tourist for lots of solves
  console.log("Total submissions:", submissions.length);
  console.log("Sample tags:", submissions[0].problem.tags);

  const tagStats: any = {};
  roadmapTopics.forEach(topic => {
    tagStats[topic] = { attempted: new Set(), solved: new Set() };
  });

  submissions.forEach(sub => {
    const probId = `${sub.problem.contestId}${sub.problem.index}`;
    const isSolved = sub.verdict === 'OK';
    
    // Check if sub.problem.tags exists
    if (!sub.problem.tags) return;

    roadmapTopics.forEach(topic => {
      const topicTags = topicToTags[topic as RoadmapTopic];
      if (sub.problem.tags.some(tag => topicTags.includes(tag))) {
        tagStats[topic].attempted.add(probId);
        if (isSolved) {
          tagStats[topic].solved.add(probId);
        }
      }
    });
  });

  console.log("Stats for DP:", tagStats["Dynamic Programming"].solved.size, "solved");
  console.log("Stats for Math (Hashing):", tagStats["Hashing"].solved.size, "solved");
}
run();
