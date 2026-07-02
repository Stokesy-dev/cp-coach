# CPCoach Web Backend 🎓

This is the Node.js backend for CPCoach Web, ported from the original LangGraph agent to a production-ready REST API. It handles user authentication via GitHub OAuth, maintains persistent user states in PostgreSQL, and provides endpoints for the Codeforces recommendation loop.

## Design Decisions
- **Persistence**: We use PostgreSQL with Prisma instead of an in-memory LangGraph state to ensure the agent's progress is saved across sessions.
- **Weakness Formula**: Retains the original attempts-weighted calculation: `W = (1 - R) * ln(1 + U)`.
- **Target Rating Initialization**: When a user's Codeforces history is synced, their 16 roadmap topics are dynamically seeded with an initial target rating based on their solved problems (tag-specific avg -> overall avg -> 800) + 100.
- **Rating-band Widening**: If the exact target rating yields 0 candidates, the search band widens iteratively by ±100 up to ±1000, eventually falling back to any unsolved matching problem to prevent crashes.

## Environment Variables
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/cpcoach?schema=public"
GITHUB_CLIENT_ID="your_github_client_id"
GITHUB_CLIENT_SECRET="your_github_client_secret"
JWT_SECRET="your_jwt_secret"
GROQ_API_KEY="your_groq_api_key"
FRONTEND_URL="http://localhost:3000"
PORT=5000
```

## Setup & Running
```bash
cd backend
npm install
npx prisma generate
npx prisma db push
npm run dev
```

## API Endpoints

### `GET /auth/github`
Redirects the user to GitHub to authorize the app.

### `GET /auth/github/callback`
Callback URL for GitHub OAuth. Issues a JWT in an `httpOnly` cookie and redirects to the frontend.

### `POST /auth/logout`
Clears the JWT authentication cookie.

---
**All `/api/*` endpoints require the JWT authentication cookie.**

### `GET /api/me`
Returns the currently authenticated user's profile.

### `POST /api/handle`
**Body:** `{ "codeforcesHandle": "tourist" }`
Links the provided Codeforces handle to the user, fetches their full submission history, and initializes or re-syncs their 16 roadmap progress topics.

### `GET /api/roadmap`
Returns the user's 16-topic roadmap progress, ranked dynamically by their weakness score from weakest to strongest.

### `POST /api/recommend`
Calculates the user's weakest topic, queries Codeforces for candidate problems, runs the rating-band search logic, and returns a single recommended problem along with an LLM-generated rationale.

### `POST /api/feedback`
**Body:** `{ "topic": "Graphs", "result": "pass" | "fail", "problemId": "1234A" }`
Records user feedback on a recommendation, dynamically adjusting the target rating and updating the attempt/solve counts for that topic.
