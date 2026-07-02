# CPCoach Web 🚀

CPCoach is a modern, full-stack web application designed to be your personal competitive programming coach. It automatically analyzes your Codeforces history, discovers your weakest areas, and provides tailored problem recommendations that dynamically adjust to your skill level.

## 🛠️ Technology Stack

This project is built using a modern, scalable JavaScript/TypeScript ecosystem:

### Frontend
- **Framework:** React + Vite
- **Styling:** Tailwind CSS + Lucide Icons
- **Deployment:** Vercel

### Backend
- **Framework:** Node.js + Express
- **Language:** TypeScript
- **Authentication:** JWT (JSON Web Tokens) with robust Email/Password flow (bcrypt hashing)
- **Deployment:** Render

### Database
- **ORM:** Prisma
- **Database:** PostgreSQL (hosted on Neon)

---

## 🌟 Key Features

1. **Secure Authentication:** 
   - Robust Email and Password registration system.
   - Secure Bearer token architecture for seamless cross-domain API calls.
2. **Codeforces Integration:** 
   - Connects directly to the public Codeforces API to ingest user submissions.
3. **Weak-Area Analysis:** 
   - Calculates weighted weakness scores based on your solve rates for specific algorithm tags (e.g., Dynamic Programming, Graphs).
4. **Dynamic Target Rating:** 
   - Recommends problems at exactly the right difficulty. Passes bump the difficulty up, failures drop it down.
5. **Modern UI:** 
   - Glassmorphism, animated transitions, and a dark-mode optimized interface built with Tailwind CSS.

---

## 🚀 Deployment Architecture

The application is deployed using a decoupled microservices architecture:

- **Frontend (Vercel):** The React application is built and served globally via Vercel's edge network. It uses environment variables (`VITE_API_URL`) to communicate securely with the backend.
- **Backend (Render):** The Express API is hosted on Render, handling all heavy computation, Codeforces API rate-limiting, and database interactions.
- **Database (Neon):** Serverless PostgreSQL database for instant scaling and secure data persistence.

---

## 💻 Local Development Setup

To run this project locally on your machine:

### 1. Database Setup
1. Create a free PostgreSQL database on [Neon](https://neon.tech).
2. Get your connection string.

### 2. Backend Setup
```bash
cd backend
npm install
```
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL="your-neon-postgres-url"
JWT_SECRET="your-secret-key"
FRONTEND_URL="http://localhost:5173"
```
Run the database migrations and start the server:
```bash
npx prisma db push
npm run dev
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_URL="http://localhost:5001"
```
Start the development server:
```bash
npm run dev
```

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

