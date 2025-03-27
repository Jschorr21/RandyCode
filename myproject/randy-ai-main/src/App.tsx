import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Auth from "./pages/Auth";
import AuthGuard from "./components/AuthGuard";
import NotFound from "./pages/NotFound";
// We'll create this next
import { AuthProvider } from "@/contexts/AuthContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<Auth />} />

          {/* Protected routes go inside AuthGuard */}
          <Route
            path="/"
            element={
              <AuthGuard>
                <Index />
              </AuthGuard>
            }
          />
          <Route
            path="*"
            element={
              <AuthGuard>
                <NotFound />
              </AuthGuard>
            }
          />
        </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
