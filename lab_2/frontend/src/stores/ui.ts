import { create } from "zustand";

interface UIState {
  sidebarCollapsed: boolean;
  concordanceWindow: number;
  selectedTextIds: number[];
  toggleSidebar: () => void;
  setConcordanceWindow: (n: number) => void;
  setSelectedTextIds: (ids: number[]) => void;
  toggleSelectedText: (id: number) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  concordanceWindow: 5,
  selectedTextIds: [],
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setConcordanceWindow: (n) => set({ concordanceWindow: n }),
  setSelectedTextIds: (ids) => set({ selectedTextIds: ids }),
  toggleSelectedText: (id) =>
    set((s) => ({
      selectedTextIds: s.selectedTextIds.includes(id)
        ? s.selectedTextIds.filter((i) => i !== id)
        : s.selectedTextIds.length < 4
        ? [...s.selectedTextIds, id]
        : s.selectedTextIds,
    })),
}));
