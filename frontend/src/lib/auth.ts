// src/lib/auth.ts
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

const SECRET_KEY = process.env.JWT_SECRET || 'your_secret_key';

export interface User {
  username: string;
  password: string;
}

export function verifyPassword(inputPassword: string, storedPassword: string): boolean {
  return bcrypt.compareSync(inputPassword, storedPassword);
}

export function generateToken(user: User): string {
  return jwt.sign({ username: user.username }, SECRET_KEY, { expiresIn: '1h' });
}

export function verifyToken(token: string): boolean {
  try {
    jwt.verify(token, SECRET_KEY);
    return true;
  } catch {
    return false;
  }
}