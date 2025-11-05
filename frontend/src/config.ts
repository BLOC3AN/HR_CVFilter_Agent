// API Configuration
// In production (Docker), nginx proxies /api and /health to backend service
// In development, use VITE_BACKEND_API_URL from .env file
export const API_BASE_URL = import.meta.env.VITE_BACKEND_API_URL || '';

