import { useCallback, useEffect, useState } from 'react';
import { authService, User } from '@/lib/auth';

interface UseCurrentUserResult {
  user: User | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<User | null>;
}

export const useCurrentUser = (): UseCurrentUserResult => {
  const [user, setUser] = useState<User | null>(authService.getCachedUser());
  const [loading, setLoading] = useState(!authService.getCachedUser());
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const profile = await authService.getProfile(true);
      setUser(profile);
      return profile;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to fetch user');
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      setLoading(false);
      return;
    }
    let mounted = true;
    (async () => {
      const profile = await authService.getProfile();
      if (!mounted) {
        return;
      }
      setUser(profile);
      setLoading(false);
    })();
    return () => {
      mounted = false;
    };
  }, [user]);

  return { user, loading, error, refresh };
};
