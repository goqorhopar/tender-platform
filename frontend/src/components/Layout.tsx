/**
 * Layout Component - Main Application Shell
 * Production-grade responsive layout with navigation
 */

import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/auth.store';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path || (path !== '/' && location.pathname.startsWith(path));
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Outlet />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Navigation */}
            <div className="flex items-center space-x-8">
              <Link to="/" className="text-xl font-bold text-blue-600">
                TenderPlatform
              </Link>
              
              <nav className="hidden md:flex space-x-4">
                <Link
                  to="/"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/')
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/tenders"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/tenders')
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  Tenders
                </Link>
                <Link
                  to="/tenders/new"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/tenders/new')
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  Create Tender
                </Link>
              </nav>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {user && (
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                    {user.full_name.charAt(0).toUpperCase()}
                  </div>
                  <span className="text-sm text-gray-700 hidden sm:block">
                    {user.full_name}
                  </span>
                </div>
              )}
              
              <Link
                to="/profile"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Profile
              </Link>
              
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-700 font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      <div className="md:hidden bg-white border-b">
        <div className="px-4 py-2 flex space-x-4 overflow-x-auto">
          <Link
            to="/"
            className={`px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap ${
              isActive('/')
                ? 'bg-blue-50 text-blue-600'
                : 'text-gray-600'
            }`}
          >
            Dashboard
          </Link>
          <Link
            to="/tenders"
            className={`px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap ${
              isActive('/tenders')
                ? 'bg-blue-50 text-blue-600'
                : 'text-gray-600'
            }`}
          >
            Tenders
          </Link>
          <Link
            to="/tenders/new"
            className={`px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap ${
              isActive('/tenders/new')
                ? 'bg-blue-50 text-blue-600'
                : 'text-gray-600'
            }`}
          >
            New Tender
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            © 2024 TenderPlatform. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
