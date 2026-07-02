import { create } from 'zustand';
import { persist } from 'zustand/middleware';
type LocalApplicationStatus = 'applied' | 'interview' | 'assessment' | 'offer' | 'rejected' | 'saved';

interface LocalApplication {
  id: string;
  jobId: number;
  title: string;
  company: string;
  status: LocalApplicationStatus;
  appliedAt: string;
  tailoredResumeId?: number;
  selectedResumeId?: number;
  selectedTailoredResumeId?: number;
  selectedCoverLetterId?: number;
  notes?: string;
}

interface ApplicationsState {
  applications: LocalApplication[];
  addApplication: (app: Omit<LocalApplication, 'id' | 'appliedAt'> & { appliedAt?: string }) => void;
  updateStatus: (id: string, status: LocalApplicationStatus) => void;
  updateSelection: (
    id: string,
    payload: Partial<Pick<LocalApplication, 'selectedResumeId' | 'selectedTailoredResumeId' | 'selectedCoverLetterId'>>,
  ) => void;
  removeApplication: (id: string) => void;
  getByStatus: (status: LocalApplicationStatus) => LocalApplication[];
}

export const useApplicationsStore = create<ApplicationsState>()(
  persist(
    (set, get) => ({
      applications: [],

      addApplication: (app) => {
        const entry: LocalApplication = {
          ...app,
          id: crypto.randomUUID(),
          appliedAt: app.appliedAt ?? new Date().toISOString(),
        };
        set({ applications: [entry, ...get().applications] });
      },

      updateStatus: (id, status) => {
        set({
          applications: get().applications.map((a) => (a.id === id ? { ...a, status } : a)),
        });
      },

      updateSelection: (id, payload) => {
        set({
          applications: get().applications.map((a) => (a.id === id ? { ...a, ...payload } : a)),
        });
      },

      removeApplication: (id) => {
        set({ applications: get().applications.filter((a) => a.id !== id) });
      },

      getByStatus: (status) => get().applications.filter((a) => a.status === status),
    }),
    { name: 'applications-store' },
  ),
);
