import { create } from "zustand";

interface UIState {
  selectedDocumentId: number | null;
  selectedSentenceId: number | null;
  isSidebarOpen: boolean;
  setSelectedDocument: (id: number | null) => void;
  setSelectedSentence: (id: number | null) => void;
  setSidebarOpen: (isOpen: boolean) => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  selectedDocumentId: null,
  selectedSentenceId: null,
  isSidebarOpen: true,
  setSelectedDocument: (id) => set({ selectedDocumentId: id }),
  setSelectedSentence: (id) => set({ selectedSentenceId: id }),
  setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
