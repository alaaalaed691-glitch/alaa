const AUTH_KEY = 'smart_platform_auth';

export function getAuth() {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setAuth(auth) {
  localStorage.setItem(AUTH_KEY, JSON.stringify(auth));
}

export function clearAuth() {
  localStorage.removeItem(AUTH_KEY);
}

export function requireAuth({ allowAnonymous = false } = {}) {
  const auth = getAuth();
  if (!auth && !allowAnonymous) {
    window.location.href = '/login';
    return null;
  }
  return auth;
}

export function isTeacher(auth) {
  return auth && (auth.role === 'teacher' || auth.role === 'admin');
}
