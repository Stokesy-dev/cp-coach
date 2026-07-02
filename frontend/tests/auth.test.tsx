import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../src/contexts/AuthContext';
import { ProtectedRoute } from '../src/components/ProtectedRoute';

vi.mock('../src/api', () => ({
  authAPI: {
    getMe: vi.fn().mockResolvedValue({ id: '1', githubId: '123', username: 'testuser', codeforcesHandle: 'tourist' })
  }
}));

describe('Auth Routing', () => {
  it('allows access to protected route if authenticated', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/dashboard" element={<ProtectedRoute><div data-testid="dashboard" /></ProtectedRoute>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('dashboard')).toBeInTheDocument();
    });
  });
});
