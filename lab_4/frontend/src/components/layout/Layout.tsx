import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { AnimatePresence, motion } from "framer-motion";
import { useLocation } from "react-router-dom";
import { PanelLeftOpen } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";

export function Layout() {
  const location = useLocation();
  const isSidebarOpen = useUIStore((state) => state.isSidebarOpen);
  const setSidebarOpen = useUIStore((state) => state.setSidebarOpen);

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <AnimatePresence initial={false}>
        {isSidebarOpen && (
          <motion.div
            key="sidebar"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -20, opacity: 0 }}
            transition={{ duration: 0.16, ease: "easeOut" }}
          >
            <Sidebar onClose={() => setSidebarOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>
      <main style={{ flex: 1, overflow: "auto", position: "relative" }}>
        {!isSidebarOpen && (
          <button
            aria-label="Open sidebar"
            className="btn btn-ghost"
            onClick={() => setSidebarOpen(true)}
            style={{
              position: "absolute",
              top: 12,
              left: 12,
              zIndex: 20,
              padding: 6,
              minWidth: "auto",
              background: "var(--surface)",
            }}
          >
            <PanelLeftOpen size={14} />
          </button>
        )}
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            style={{ minHeight: "100%" }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
