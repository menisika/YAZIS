import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { LibraryPage } from "@/pages/LibraryPage";
import { ExplorerPage } from "@/pages/ExplorerPage";
import { TreeViewPage } from "@/pages/TreeViewPage";
import { HeatmapPage } from "@/pages/HeatmapPage";
import { PatternSearchPage } from "@/pages/PatternSearchPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<LibraryPage />} />
            <Route path="documents/:id" element={<ExplorerPage />} />
            <Route path="documents/:id/sentences/:sentenceId" element={<TreeViewPage />} />
            <Route path="documents/:id/heatmap" element={<HeatmapPage />} />
            <Route path="patterns" element={<PatternSearchPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
