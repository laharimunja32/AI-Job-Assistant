import { useQuery } from '@tanstack/react-query';
import { profileService } from '@/services';

export const profileKeys = {
  all: ['profile'] as const,
  current: () => [...profileKeys.all, 'current'] as const,
};

export function useProfile() {
  return useQuery({
    queryKey: profileKeys.current(),
    queryFn: async () => {
      const { data } = await profileService.get();
      return data;
    },
  });
}
