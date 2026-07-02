# CPCoach Web Frontend 🎓

This is the React (Vite) frontend for CPCoach Web, built with a premium glassmorphic dark-mode aesthetic using Tailwind CSS.

## Features
- **GitHub OAuth Login**: Clean landing page that routes you to the backend's GitHub OAuth flow.
- **Codeforces Sync**: Connect your handle to fetch and analyze your entire submission history.
- **Dynamic Weakness Dashboard**: A visual representation of your roadmap progress, identifying exactly what topics you struggle with most.
- **Smart Recommendations**: Get single-problem recommendations targeting your weakest topics, complete with an AI rationale.
- **Feedback Loop**: Mark problems as Solved/Failed to instantly adjust your target difficulty.

## Setup & Running
1. Install dependencies:
   ```bash
   npm install
   ```
2. Set your environment variables in `.env`:
   ```env
   VITE_API_URL="http://localhost:5000"
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Architecture
- **Auth Flow**: The backend manages the JWT via an `httpOnly` cookie. The frontend checks `GET /api/me` on load via the `AuthContext` to determine if the user is authenticated.
- **API Centralization**: All API calls are located in `src/api.ts` and configured to send credentials (cookies) automatically.
- **State & Routing**: React Router is used with a `ProtectedRoute` wrapper that gates the dashboard and settings based on auth and codeforces handle presence.

## Testing
Unit and component tests are written using Vitest and React Testing Library.
```bash
npm test
```
