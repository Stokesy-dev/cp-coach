import { PrismaClient } from '@prisma/client';

// Single shared PrismaClient instance to avoid connection pool exhaustion (H-6)
const prisma = new PrismaClient();

export default prisma;
