import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import authRoutes from './routes/auth';
import apiRoutes from './routes/api';

const app = express();

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));

app.use(express.json());
app.use(cookieParser());

app.use('/auth', authRoutes);
app.use('/api', apiRoutes);

app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error('Unhandled error:', err);
  const status = err.status || 500;
  const message = err.message || 'Internal Server Error';
  res.status(status).json({ error: message });
});

export default app;
