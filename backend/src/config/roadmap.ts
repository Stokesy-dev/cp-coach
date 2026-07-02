export const roadmapTopics = [
  "Arrays & Strings",
  "Hashing",
  "Two Pointers",
  "Sliding Window",
  "Binary Search",
  "Stack & Queue",
  "Linked List",
  "Trees & BST",
  "Heap",
  "Backtracking",
  "Graphs",
  "Dynamic Programming",
  "Trie",
  "Union Find (DSU)",
  "Segment Tree (basic)",
  "Bit Manipulation"
] as const;

export type RoadmapTopic = typeof roadmapTopics[number];

export const topicToTags: Record<RoadmapTopic, string[]> = {
  "Arrays & Strings": ["implementation", "strings", "sortings"],
  "Hashing": ["hashing", "math"],
  "Two Pointers": ["two pointers"],
  "Sliding Window": ["two pointers"],
  "Binary Search": ["binary search"],
  "Stack & Queue": ["data structures"],
  "Linked List": ["data structures"],
  "Trees & BST": ["trees", "dfs and similar"],
  "Heap": ["data structures"],
  "Backtracking": ["brute force", "dfs and similar"],
  "Graphs": ["graphs", "dfs and similar", "shortest paths"],
  "Dynamic Programming": ["dp"],
  "Trie": ["strings", "data structures", "trees"],
  "Union Find (DSU)": ["dsu"],
  "Segment Tree (basic)": ["data structures", "trees"],
  "Bit Manipulation": ["bitmasks"]
};
