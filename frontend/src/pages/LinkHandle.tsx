import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userAPI } from '../api';
import { useNavigate, Navigate } from 'react-router-dom';
import { User, Loader2, AlertCircle } from 'lucide-react';

export default function LinkHandle() {
  const { user, checkAuth } = useAuth();
  const [handle, setHandle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  if (user && user.codeforcesHandle) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!handle.trim()) return;

    setLoading(true);
    setError('');

    try {
      await userAPI.linkHandle(handle.trim());
      await checkAuth();
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to link handle. Make sure the handle exists on Codeforces.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 animate-fade-in relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[60%] rounded-full bg-secondary/10 blur-[150px] pointer-events-none" />
      
      <div className="glass-card max-w-md w-full p-8 relative z-10 animate-slide-up">
        <h2 className="text-2xl font-bold mb-2 text-white text-center">Connect Codeforces</h2>
        <p className="text-slate-400 text-center mb-8">
          Enter your Codeforces handle so we can fetch your submission history and initialize your roadmap.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-accent/10 border border-accent/20 rounded-lg flex items-start gap-3 text-accent">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Codeforces Handle
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-slate-500" />
              </div>
              <input
                type="text"
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                className="glass-input pl-10"
                placeholder="e.g. tourist"
                required
                disabled={loading}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !handle.trim()}
            className="glass-button w-full flex items-center justify-center py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                Syncing History... (This may take a moment)
              </>
            ) : (
              'Sync Handle'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
