import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userAPI } from '../api';
import { useNavigate } from 'react-router-dom';
import { User, Loader2, AlertCircle, ArrowLeft } from 'lucide-react';

export default function Settings() {
  const { user, checkAuth } = useAuth();
  const [handle, setHandle] = useState(user?.codeforcesHandle || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

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
      setError(err.response?.data?.error || 'Failed to update handle.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 relative">
      <button onClick={() => navigate('/dashboard')} className="glass-button-secondary mb-8 flex items-center gap-2">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div className="glass-card max-w-md w-full p-8 mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-white">Settings</h2>
        
        {error && (
          <div className="mb-6 p-4 bg-accent/10 border border-accent/20 rounded-lg flex items-start gap-3 text-accent">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Update Codeforces Handle
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
                required
                disabled={loading}
              />
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Updating your handle will re-sync your entire Codeforces history.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !handle.trim() || handle.trim() === user?.codeforcesHandle}
            className="glass-button w-full flex items-center justify-center py-3 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  );
}
