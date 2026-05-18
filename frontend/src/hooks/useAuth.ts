/**
 * useAuth Hook - Authentication State Management
 * Production-grade hook for auth state access
 */

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/auth.store';

export function useAuth() {
  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading, error, logout, checkAuth } = useAuthStore();

  const handleLogout = useCallback(async () => {
    logout();
    navigate('/login');
  }, [logout, navigate]);

  const refreshAuth = useCallback(async () => {
    return await checkAuth();
  }, [checkAuth]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    logout: handleLogout,
    refreshAuth,
  };
}

export default useAuth;
