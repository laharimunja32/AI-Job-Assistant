import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  recruitmentMonitoringService,
  type AssessmentPayload,
  type EmailProcessPayload,
  type InterviewPayload,
  type InterviewUpdatePayload,
  type ReminderPayload,
} from '@/services';

const keys = {
  all: ['recruitment-monitoring'] as const,
  emails: (params: Record<string, unknown>) => [...keys.all, 'emails', params] as const,
  assessments: (params: Record<string, unknown>) => [...keys.all, 'assessments', params] as const,
  interviews: (params: Record<string, unknown>) => [...keys.all, 'interviews', params] as const,
  timeline: (applicationId: number) => [...keys.all, 'timeline', applicationId] as const,
  reminders: (params: Record<string, unknown>) => [...keys.all, 'reminders', params] as const,
  notifications: (params: Record<string, unknown>) => [...keys.all, 'notifications', params] as const,
};

export function useRecruitmentEmails(page = 1, size = 20) {
  return useQuery({
    queryKey: keys.emails({ page, size }),
    queryFn: async () => (await recruitmentMonitoringService.listEmails({ page, size })).data,
  });
}

export function useProcessRecruitmentEmail() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: EmailProcessPayload) => recruitmentMonitoringService.processEmail(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.all }),
  });
}

export function useAssessments(page = 1, size = 20, status?: string) {
  return useQuery({
    queryKey: keys.assessments({ page, size, status }),
    queryFn: async () => (await recruitmentMonitoringService.listAssessments({ page, size, status })).data,
  });
}

export function useCreateAssessment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: AssessmentPayload) => recruitmentMonitoringService.createAssessment(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.all }),
  });
}

export function useUpdateAssessment(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: AssessmentPayload) => recruitmentMonitoringService.updateAssessment(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.all }),
  });
}

export function useInterviews(page = 1, size = 20, status?: string) {
  return useQuery({
    queryKey: keys.interviews({ page, size, status }),
    queryFn: async () => (await recruitmentMonitoringService.listInterviews({ page, size, status })).data,
  });
}

export function useCreateInterview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: InterviewPayload) => recruitmentMonitoringService.createInterview(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.all }),
  });
}

export function useUpdateInterview(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: InterviewUpdatePayload) => recruitmentMonitoringService.updateInterview(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.all }),
  });
}

export function useTimeline(applicationId: number) {
  return useQuery({
    queryKey: keys.timeline(applicationId),
    queryFn: async () => (await recruitmentMonitoringService.getTimeline(applicationId)).data,
    enabled: applicationId > 0,
  });
}

export function useReminders(page = 1, size = 20) {
  return useQuery({
    queryKey: keys.reminders({ page, size }),
    queryFn: async () => (await recruitmentMonitoringService.listReminders({ page, size })).data,
  });
}

export function useCreateReminder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ReminderPayload) => recruitmentMonitoringService.createReminder(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.all }),
  });
}

export function useUpdateReminder(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<ReminderPayload> & { is_completed?: boolean }) =>
      recruitmentMonitoringService.updateReminder(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.all }),
  });
}

export function useDeleteReminder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => recruitmentMonitoringService.deleteReminder(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.all }),
  });
}

export function useNotificationHistory(page = 1, size = 20) {
  return useQuery({
    queryKey: keys.notifications({ page, size }),
    queryFn: async () => (await recruitmentMonitoringService.listNotificationHistory({ page, size })).data,
  });
}
