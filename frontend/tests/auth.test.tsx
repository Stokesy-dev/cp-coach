import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../src/contexts/AuthContext';
import { ProtectedRoute } from '../src/components/ProtectedRoute';

vi.mock('../src/api', () => ({
  authAPI: {
    getMe: vi.fn().mockResolvedValue({ id: '1', email: 'test@test.com', username: 'testuser', codeforcesHandle: 'tourist' })
  }
}));

// Provide a localStorage mock for the test environment
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();

Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock, writable: true });

describe('Auth Routing', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('allows access to protected route if authenticated', async () => {
    // H-4: checkAuth now checks for a token before calling getMe
    localStorageMock.setItem('token', 'fake-jwt-token');

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/" element={<div data-testid="login" />} />
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
