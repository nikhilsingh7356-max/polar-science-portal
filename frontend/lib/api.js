export const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export function assetUrl(path) {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return `${API}${path.startsWith('/') ? path : `/${path}`}`;
}
export async function api(path, options = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const headers = { ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  const r = await fetch(`${API}${path}`, { ...options, headers, cache: 'no-store' });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || 'Request failed');
  return data;
}
