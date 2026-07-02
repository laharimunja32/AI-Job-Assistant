import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { browserService } from '@/services';
import type { BrowserType } from '@/types';

export const browserKeys = {
  all: ['browser'] as const,
  sessions: () => [...browserKeys.all, 'sessions'] as const,
  session: (sessionId: string) => [...browserKeys.all, 'session', sessionId] as const,
  status: () => [...browserKeys.all, 'status'] as const,
  formDetection: (sessionId: string) => [...browserKeys.all, 'forms', 'detect', sessionId] as const,
  formReport: (sessionId: string) => [...browserKeys.all, 'forms', 'report', sessionId] as const,
  uploadDetection: (sessionId: string) => [...browserKeys.all, 'uploads', 'detect', sessionId] as const,
  uploadStatus: (sessionId: string, applicationId: number) => [...browserKeys.all, 'uploads', 'status', sessionId, applicationId] as const,
  review: (sessionId: string) => [...browserKeys.all, 'review', sessionId] as const,
  reviewValidation: (sessionId: string) => [...browserKeys.all, 'review-validation', sessionId] as const,
  reviewHistory: (applicationId: number) => [...browserKeys.all, 'review-history', applicationId] as const,
};

export function useBrowserSessions() {
  return useQuery({
    queryKey: browserKeys.sessions(),
    queryFn: async () => {
      const { data } = await browserService.listSessions();
      return data;
    },
    refetchInterval: 10_000,
  });
}

export function useBrowserStatus() {
  return useQuery({
    queryKey: browserKeys.status(),
    queryFn: async () => {
      const { data } = await browserService.getStatus();
      return data;
    },
    refetchInterval: 10_000,
  });
}

export function useCreateBrowserSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload?: { browser_type?: BrowserType; application_id?: number }) =>
      browserService.createSession(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useOpenApplicationInBrowser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ applicationId, sessionId, browserType }: { applicationId: number; sessionId?: string; browserType?: BrowserType }) =>
      browserService.openApplication(applicationId, { session_id: sessionId, browser_type: browserType }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useCloseBrowserSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => browserService.closeSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useRestartBrowserSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, browserType }: { sessionId: string; browserType?: BrowserType }) =>
      browserService.restartSession(sessionId, { browser_type: browserType }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useDetectFormFields() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => browserService.detectFormFields(sessionId),
    onSuccess: (_, sessionId) => {
      queryClient.invalidateQueries({ queryKey: browserKeys.formDetection(sessionId) });
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useFillFormFields() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      overrides,
      traverseSteps,
    }: {
      sessionId: string;
      overrides?: Record<string, string>;
      traverseSteps?: boolean;
    }) => browserService.fillFormFields(sessionId, { overrides, traverse_steps: traverseSteps }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: browserKeys.formReport(variables.sessionId) });
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useFormFillReport(sessionId?: string) {
  return useQuery({
    queryKey: browserKeys.formReport(sessionId || 'none'),
    queryFn: async () => {
      if (!sessionId) {
        throw new Error('Session ID is required');
      }
      const { data } = await browserService.getFormReport(sessionId);
      return data;
    },
    enabled: Boolean(sessionId),
    retry: false,
  });
}

export function useDetectUploadFields() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => browserService.detectUploadFields(sessionId),
    onSuccess: (_, sessionId) => {
      queryClient.invalidateQueries({ queryKey: browserKeys.uploadDetection(sessionId) });
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useUploadAllDocuments() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      applicationId,
      useTailoredResume,
      forceRedetect,
    }: {
      sessionId: string;
      applicationId: number;
      useTailoredResume?: boolean;
      forceRedetect?: boolean;
    }) =>
      browserService.uploadAll(sessionId, {
        application_id: applicationId,
        use_tailored_resume: useTailoredResume,
        force_redetect: forceRedetect,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: browserKeys.uploadStatus(variables.sessionId, variables.applicationId) });
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useRetryUpload() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      applicationId,
      includeResume,
      includeCoverLetter,
    }: {
      sessionId: string;
      applicationId: number;
      includeResume?: boolean;
      includeCoverLetter?: boolean;
    }) =>
      browserService.retryUpload(sessionId, {
        application_id: applicationId,
        include_resume: includeResume,
        include_cover_letter: includeCoverLetter,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: browserKeys.uploadStatus(variables.sessionId, variables.applicationId) });
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useUploadStatus(sessionId?: string, applicationId?: number) {
  return useQuery({
    queryKey: browserKeys.uploadStatus(sessionId || 'none', applicationId || 0),
    queryFn: async () => {
      if (!sessionId || !applicationId) {
        throw new Error('Session and application are required');
      }
      const { data } = await browserService.getUploadStatus(sessionId, applicationId);
      return data;
    },
    enabled: Boolean(sessionId && applicationId),
    retry: false,
  });
}

export function useBrowserReview(sessionId?: string) {
  return useQuery({
    queryKey: browserKeys.review(sessionId || 'none'),
    queryFn: async () => {
      if (!sessionId) throw new Error('Session is required');
      const { data } = await browserService.getReview(sessionId);
      return data;
    },
    enabled: Boolean(sessionId),
    retry: false,
  });
}

export function useValidateBrowserReview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => browserService.validateReview(sessionId),
    onSuccess: (_, sessionId) => {
      queryClient.invalidateQueries({ queryKey: browserKeys.reviewValidation(sessionId) });
      queryClient.invalidateQueries({ queryKey: browserKeys.review(sessionId) });
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useConfirmBrowserReview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      confirmed,
      attemptSubmission,
      reviewTimeSeconds,
    }: {
      sessionId: string;
      confirmed: boolean;
      attemptSubmission?: boolean;
      reviewTimeSeconds?: number;
    }) =>
      browserService.confirmReview(sessionId, {
        confirmed,
        attempt_submission: attemptSubmission,
        review_time_seconds: reviewTimeSeconds,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: browserKeys.review(variables.sessionId) });
      queryClient.invalidateQueries({ queryKey: browserKeys.all });
    },
  });
}

export function useReviewHistory(applicationId?: number) {
  return useQuery({
    queryKey: browserKeys.reviewHistory(applicationId || 0),
    queryFn: async () => {
      if (!applicationId) throw new Error('Application required');
      const { data } = await browserService.getReviewHistory(applicationId);
      return data;
    },
    enabled: Boolean(applicationId),
    retry: false,
  });
}
