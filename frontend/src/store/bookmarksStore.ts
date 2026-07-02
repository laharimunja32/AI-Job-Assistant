import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface BookmarkedJob {
  id: number;
  title: string;
  company: string;
  savedAt: string;
}

interface BookmarksState {
  bookmarks: BookmarkedJob[];
  isBookmarked: (jobId: number) => boolean;
  toggleBookmark: (job: { id: number; title: string; company: string }) => void;
  removeBookmark: (jobId: number) => void;
}

export const useBookmarksStore = create<BookmarksState>()(
  persist(
    (set, get) => ({
      bookmarks: [],

      isBookmarked: (jobId) => get().bookmarks.some((b) => b.id === jobId),

      toggleBookmark: (job) => {
        const exists = get().isBookmarked(job.id);
        if (exists) {
          set({ bookmarks: get().bookmarks.filter((b) => b.id !== job.id) });
        } else {
          set({
            bookmarks: [
              { id: job.id, title: job.title, company: job.company, savedAt: new Date().toISOString() },
              ...get().bookmarks,
            ],
          });
        }
      },

      removeBookmark: (jobId) => {
        set({ bookmarks: get().bookmarks.filter((b) => b.id !== jobId) });
      },
    }),
    { name: 'bookmarks-store' },
  ),
);
