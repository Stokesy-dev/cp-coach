import { authAPI } from '../api';
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import { LogIn, Code2 } from 'lucide-react';

export default function Login() {
  const { user } = useAuth();

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleLogin = () => {
    window.location.href = authAPI.getGitHubLoginUrl();
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 animate-fade-in relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-accent/20 blur-[120px] pointer-events-none" />

      <div className="glass-card max-w-md w-full p-8 text-center relative z-10 animate-slide-up">
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-primary/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-primary/30">
            <Code2 className="w-8 h-8 text-primary" />
          </div>
        </div>
        <h1 className="text-3xl font-bold mb-4 text-white">CPCoach Web</h1>
        <p className="text-slate-300 mb-8 leading-relaxed">
          Your personal competitive programming coach. Automatically analyze your Codeforces history, discover your weakest areas, and get tailored problem recommendations that dynamically adjust to your skill level.
        </p>
        
        <button
          onClick={handleLogin}
          className="glass-button w-full flex items-center justify-center gap-3 text-lg py-3"
        >
          <LogIn className="w-5 h-5" />
          Sign in with GitHub
        </button>
      </div>
    </div>
  );
}
