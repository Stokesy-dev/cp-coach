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

export async function fetchUserSubmissions(handle: string): Promise<CFSubmission[]> {
  try {
    const response = await axios.get(`${CF_API_BASE}/user.status`, {
      params: { handle }
    });
    if (response.data.status === 'OK') {
      return response.data.result;
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
  try {
    const response = await axios.get(`${CF_API_BASE}/problemset.problems`);
    if (response.data.status === 'OK') {
      return response.data.result.problems;
    }
    throw new Error(response.data.comment || 'Failed to fetch problems');
  } catch (error: any) {
    throw new Error(`Codeforces API Error: ${error.message}`);
  }
}
