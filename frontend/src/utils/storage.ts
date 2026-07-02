const STORAGE_PREFIX = 'ai-job-assistant:';

export function storageGet<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(`${STORAGE_PREFIX}${key}`);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export function storageSet<T>(key: string, value: T): void {
  localStorage.setItem(`${STORAGE_PREFIX}${key}`, JSON.stringify(value));
}

export function storageRemove(key: string): void {
  localStorage.removeItem(`${STORAGE_PREFIX}${key}`);
}
