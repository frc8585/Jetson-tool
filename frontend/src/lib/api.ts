// src/lib/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function fetchRobotStatus() {
  try {
    const response = await axios.get(`${API_BASE_URL}/robot/status`);
    return response.data;
  } catch (error) {
    console.error('Error fetching robot status:', error);
    throw error;
  }
}

export async function updateRobotSettings(settings: unknown, token: string) {
  try {
    const response = await axios.post(`${API_BASE_URL}/robot/settings`, settings, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    console.error('Error updating robot settings:', error);
    throw error;
  }
}