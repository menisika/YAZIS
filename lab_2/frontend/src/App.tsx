import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { CorpusPage } from "@/pages/CorpusPage";
import { TextDetailPage } from "@/pages/TextDetailPage";
import { ConcordancePage } from "@/pages/ConcordancePage";
import { FrequenciesPage } from "@/pages/FrequenciesPage";
import { MorphologyPage } from "@/pages/MorphologyPage";
import { SemanticSearchPage } from "@/pages/SemanticSearchPage";
import { StyleLabPage } from "@/pages/StyleLabPage";

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
            <Route index element={<Navigate to="/corpus" replace />} />
            <Route path="corpus" element={<CorpusPage />} />
            <Route path="corpus/:id" element={<TextDetailPage />} />
            <Route path="concordance" element={<ConcordancePage />} />
            <Route path="frequencies" element={<FrequenciesPage />} />
            <Route path="morphology" element={<MorphologyPage />} />
            <Route path="semantic" element={<SemanticSearchPage />} />
            <Route path="style-lab" element={<StyleLabPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
