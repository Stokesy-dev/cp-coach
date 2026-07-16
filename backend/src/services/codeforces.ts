import axios from 'axios';

const CF_API_BASE = 'https://codeforces.com/api';

export interface CFSubmission {
  id: number;
  contestId?: number;
  creationTimeSeconds: number;
  problem: {
    contestId?: number;
    index: string;
    name: string;
    rating?: number;
    tags: string[];
  };
  author: {
    handle: string;
  };
  programmingLanguage: string;
  verdict?: string;
  testset?: string;
  passedTestCount: number;
  timeConsumedMillis: number;
  memoryConsumedBytes: number;
}

// In-memory caches and TTLs
interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const PROBLEMS_CACHE_TTL_MS = 12 * 60 * 60 * 1000; // 12 hours
const SUBMISSIONS_CACHE_TTL_MS = 1 * 60 * 1000;    // 1 minute

let problemsCache: CacheEntry<CFProblem[]> | null = null;
const submissionsCacheMap = new Map<string, CacheEntry<CFSubmission[]>>();

export async function fetchUserSubmissions(handle: string): Promise<CFSubmission[]> {
  const now = Date.now();
  const normalizedHandle = handle.toLowerCase().trim();
  const cached = submissionsCacheMap.get(normalizedHandle);

  if (cached && now - cached.timestamp < SUBMISSIONS_CACHE_TTL_MS) {
    return cached.data;
  }

  try {
    const response = await axios.get(`${CF_API_BASE}/user.status`, {
      params: { handle }
    });
    if (response.data.status === 'OK') {
      const submissions = response.data.result;
      submissionsCacheMap.set(normalizedHandle, {
        data: submissions,
        timestamp: now
      });
      return submissions;
    }
    throw new Error(response.data.comment || 'Failed to fetch user submissions');
  } catch (error: any) {
    throw new Error(`Codeforces API Error: ${error.message}`);
  }
}

export interface CFProblem {
  contestId?: number;
  index: string;
  name: string;
  rating?: number;
  tags: string[];
}

export async function fetchAllProblems(): Promise<CFProblem[]> {
  const now = Date.now();

  if (problemsCache && now - problemsCache.timestamp < PROBLEMS_CACHE_TTL_MS) {
    return problemsCache.data;
  }

  try {
    const response = await axios.get(`${CF_API_BASE}/problemset.problems`);
    if (response.data.status === 'OK') {
      const problems = response.data.result.problems;
      problemsCache = {
        data: problems,
        timestamp: now
      };
      return problems;
    }
    throw new Error(response.data.comment || 'Failed to fetch problems');
  } catch (error: any) {
    throw new Error(`Codeforces API Error: ${error.message}`);
  }
}

