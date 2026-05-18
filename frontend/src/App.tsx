/**
 * Tender Platform - Main App Component
 * Production-grade routing and layout structure
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/auth.store';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import TendersPage from './pages/TendersPage';
import TenderDetailPage from './pages/TenderDetailPage';
import CreateTenderPage from './pages/CreateTenderPage';
import ProfilePage from './pages/ProfilePage';
import NotFoundPage from './pages/NotFoundPage';

// Protected route component
interface ProtectedRouteProps {
  children: React.ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="tenders" element={<TendersPage />} />
        <Route path="tenders/:id" element={<TenderDetailPage />} />
        <Route path="tenders/new" element={<CreateTenderPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>

      {/* 404 page */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default App;
