import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../src/contexts/AuthContext';
import Dashboard from '../src/pages/Dashboard';

vi.mock('../src/api', () => ({
  authAPI: {
    getMe: vi.fn().mockResolvedValue({ id: '1', githubId: '123', username: 'testuser', codeforcesHandle: 'tourist', avatarUrl: '' }),
    logout: vi.fn()
  },
  roadmapAPI: {
    getRoadmap: vi.fn().mockResolvedValue([
      { topic: 'Graphs', attemptedCount: 10, solvedCount: 2, targetRating: 1200, weaknessScore: 1.5 }
    ]),
    getRecommendation: vi.fn().mockResolvedValue({
      title: 'Graph Problem',
      url: 'https://codeforces.com',
      rating: 1200,
      topic: 'Graphs',
      tags: ['graphs'],
      rationale: 'Test rationale',
      problemId: '123A'
    }),
    submitFeedback: vi.fn().mockResolvedValue({ message: 'Success' })
  }
}));

describe('Dashboard component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders recommendation and submits feedback', async () => {
    const { roadmapAPI } = await import('../src/api');

    render(
      <AuthProvider>
        <MemoryRouter>
          <Dashboard />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Get Recommendation')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Get Recommendation'));

    await waitFor(() => {
      expect(screen.getByText('Graph Problem')).toBeInTheDocument();
      expect(screen.getByText(/Test rationale/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Solved'));

    await waitFor(() => {
      expect(roadmapAPI.submitFeedback).toHaveBeenCalledWith('Graphs', 'pass', '123A');
    });
  });
});
