import { Capacitor } from '@capacitor/core';
const configured = import.meta.env.VITE_API_BASE_URL?.trim();
export const API_ORIGIN = (configured || (Capacitor.isNativePlatform() ? 'https://calendar.sigq.in' : '')).replace(/\/$/, '');
export function apiUrl(path: string): string {
  return `${API_ORIGIN}${path}`;
}
