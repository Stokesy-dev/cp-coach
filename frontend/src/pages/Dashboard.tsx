import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { roadmapAPI, Recommendation } from '../api';
import { useNavigate } from 'react-router-dom';
import { LogOut, Settings as SettingsIcon, BrainCircuit, ExternalLink, Check, X, Loader2, AlertCircle } from 'lucide-react';

interface RoadmapItem {
  topic: string;
  attemptedCount: number;
  solvedCount: number;
  targetRating: number;
  weaknessScore: number;
}

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [roadmap, setRoadmap] = useState<RoadmapItem[]>([]);
  const [loadingRoadmap, setLoadingRoadmap] = useState(true);
  
  // L-4: Properly typed recommendation state
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [loadingRec, setLoadingRec] = useState(false);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  
  // C-3: Error state for user-visible error messages
  const [error, setError] = useState<string | null>(null);

  const fetchRoadmap = async () => {
    try {
      const data = await roadmapAPI.getRoadmap();
      setRoadmap(data);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to load roadmap data.');
    } finally {
      setLoadingRoadmap(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const handleGetRecommendation = async () => {
    setLoadingRec(true);
    setError(null);
    try {
      const data = await roadmapAPI.getRecommendation();
      setRecommendation(data);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to get recommendation. The server may be waking up — please try again in a moment.');
    } finally {
      setLoadingRec(false);
    }
  };

  const handleFeedback = async (result: 'pass' | 'fail') => {
    if (!recommendation) return;
    setSubmittingFeedback(true);
    setError(null);
    try {
      await roadmapAPI.submitFeedback(recommendation.topic, result, recommendation.problemId);
      setRecommendation(null);
      await fetchRoadmap();
    } catch (err: any) {
      console.error(err);
      // C-3: Show the error to the user instead of swallowing it silently
      setError(err.response?.data?.error || 'Failed to submit feedback. Please try again.');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const maxScore = Math.max(...roadmap.map(r => r.weaknessScore), 1);

  return (
    <div className="min-h-screen p-4 md:p-8 animate-fade-in">
      <header className="glass-card p-6 mb-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          {/* L-1: Avatar with fallback */}
          <img 
            src={user?.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=fallback`} 
            alt={`${user?.username || 'User'}'s avatar`}
            className="w-12 h-12 rounded-full border-2 border-primary/50"
            onError={(e) => { (e.target as HTMLImageElement).src = `https://api.dicebear.com/7.x/avataaars/svg?seed=fallback`; }}
          />
          <div>
            <h1 className="text-xl font-bold text-white">{user?.username}</h1>
            <p className="text-slate-400 text-sm">Codeforces: {user?.codeforcesHandle}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/settings')} className="glass-button-secondary flex items-center gap-2">
            <SettingsIcon className="w-4 h-4" /> Settings
          </button>
          <button onClick={logout} className="glass-button-secondary !bg-accent/10 !text-accent hover:!bg-accent/20 border-accent/20 flex items-center gap-2">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </header>

      {/* C-3: User-visible error banner */}
      {error && (
        <div className="glass-card !bg-red-500/10 !border-red-500/30 p-4 mb-8 flex items-start gap-3" role="alert" aria-live="assertive">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <BrainCircuit className="text-primary w-5 h-5" /> Topic Weakness Analysis
            </h2>
            
            {loadingRoadmap ? (
              <div className="flex justify-center p-8"><Loader2 className="animate-spin text-primary w-8 h-8" /></div>
            ) : (
              <div className="space-y-4">
                {roadmap.map((item) => (
                  <div key={item.topic} className="flex flex-col gap-1 group">
                    <div className="flex justify-between text-sm text-slate-300">
                      <span className="font-medium group-hover:text-primary transition-colors">{item.topic}</span>
                      <span>Target: {item.targetRating} ({item.solvedCount}/{item.attemptedCount} solves)</span>
                    </div>
                    <div className="w-full bg-surface rounded-full h-2.5 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-primary to-secondary h-2.5 rounded-full transition-all duration-500 ease-out" 
                        style={{ width: `${Math.max((item.weaknessScore / maxScore) * 100, 2)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6" aria-live="polite">
          <div className="glass-card p-6">
            <h2 className="text-xl font-bold text-white mb-6">Current Training</h2>
            
            {!recommendation && !loadingRec && (
              <div className="text-center py-8">
                <p className="text-slate-400 mb-6">Ready for your next challenge?</p>
                {/* M-3: Button is disabled instead of hidden during loading to prevent double-clicks */}
                <button 
                  onClick={handleGetRecommendation} 
                  disabled={loadingRec}
                  className="glass-button w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Get Recommendation
                </button>
              </div>
            )}

            {loadingRec && (
              <div className="flex flex-col items-center justify-center py-12 gap-4">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <p className="text-slate-400 animate-pulse">Analyzing weaknesses...</p>
              </div>
            )}

            {recommendation && !loadingRec && (
              <div className="animate-slide-up space-y-6">
                <div className="p-5 rounded-xl bg-surface/50 border border-white/5 space-y-4">
                  <div className="flex justify-between items-start gap-4">
                    <h3 className="font-bold text-lg text-white leading-tight">{recommendation.title}</h3>
                    <span className="px-2.5 py-1 rounded-md bg-secondary/20 text-secondary text-xs font-bold whitespace-nowrap">
                      {recommendation.rating || 'Unrated'}
                    </span>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 rounded text-xs bg-primary/20 text-primary border border-primary/20">
                      Target: {recommendation.topic}
                    </span>
                    {recommendation.tags.slice(0, 3).map((t: string) => (
                      <span key={t} className="px-2 py-1 rounded text-xs bg-white/5 text-slate-300">
                        {t}
                      </span>
                    ))}
                  </div>

                  <p className="text-sm text-slate-300 italic border-l-2 border-primary/50 pl-3">
                    "{recommendation.rationale}"
                  </p>

                  <a 
                    href={recommendation.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 w-full py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors text-sm font-medium"
                  >
                    Open Problem on Codeforces <ExternalLink className="w-4 h-4" />
                  </a>
                </div>

                <div className="space-y-3">
                  <p className="text-sm text-center text-slate-400">Did you solve it?</p>
                  <div className="grid grid-cols-2 gap-4">
                    <button 
                      onClick={() => handleFeedback('pass')}
                      disabled={submittingFeedback}
                      className="glass-button !bg-secondary/90 hover:!bg-secondary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {submittingFeedback ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />} Solved
                    </button>
                    <button 
                      onClick={() => handleFeedback('fail')}
                      disabled={submittingFeedback}
                      className="glass-button !bg-accent/90 hover:!bg-accent flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {submittingFeedback ? <Loader2 className="w-4 h-4 animate-spin" /> : <X className="w-4 h-4" />} Failed
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
