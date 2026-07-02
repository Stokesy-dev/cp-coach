import { Router } from 'express';
import axios from 'axios';
import jwt from 'jsonwebtoken';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

router.get('/github', (req, res) => {
  const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID;
  const redirectUri = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&scope=read:user`;
  res.redirect(redirectUri);
});

router.get('/github/callback', async (req, res, next) => {
  const { code } = req.query;
  if (!code) {
    res.status(400).json({ error: 'No code provided' });
    return;
  }

  try {
    const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID;
    const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET;
    const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
    const JWT_SECRET = process.env.JWT_SECRET || 'secret';

    const tokenResponse = await axios.post(
      'https://github.com/login/oauth/access_token',
      {
        client_id: GITHUB_CLIENT_ID,
        client_secret: GITHUB_CLIENT_SECRET,
        code
      },
      {
        headers: { Accept: 'application/json' }
      }
    );

    const accessToken = tokenResponse.data.access_token;
    if (!accessToken) {
      res.status(400).json({ error: 'Failed to obtain access token' });
      return;
    }

    const userResponse = await axios.get('https://api.github.com/user', {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    
    const { id, login, avatar_url } = userResponse.data;
    const githubId = String(id);

    const user = await prisma.user.upsert({
      where: { githubId },
      update: {
        username: login,
        avatarUrl: avatar_url
      },
      create: {
        githubId,
        username: login,
        avatarUrl: avatar_url
      }
    });

    const token = jwt.sign(
      { id: user.id, githubId: user.githubId },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 7 * 24 * 60 * 60 * 1000
    });

    res.redirect(FRONTEND_URL);
  } catch (error) {
    next(error);
  }
});

router.post('/logout', (req, res) => {
  res.clearCookie('token');
  res.json({ message: 'Logged out successfully' });
});

export default router;
