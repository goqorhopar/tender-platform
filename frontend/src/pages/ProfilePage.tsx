/**
 * ProfilePage - User Profile Management
 * Production-grade profile form with validation
 */

import { useState } from 'react';
import { useAuthStore } from '../store/auth.store';

export default function ProfilePage() {
  const { user, updateUser, isLoading, error, clearError } = useAuthStore();
  
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.full_name) {
      errors.full_name = 'Full name is required';
    } else if (formData.full_name.length < 2) {
      errors.full_name = 'Name must be at least 2 characters';
    }
    
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Invalid email format';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setSuccessMessage('');
    
    if (!validateForm()) return;
    
    setIsSaving(true);
    
    // Simulate API call
    setTimeout(() => {
      updateUser({ full_name: formData.full_name, email: formData.email });
      setIsSaving(false);
      setSuccessMessage('Profile updated successfully!');
    }, 500);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (validationErrors[name]) {
      setValidationErrors((prev) => ({ ...prev, [name]: '' }));
    }
    if (successMessage) {
      setSuccessMessage('');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage your account settings and preferences.
        </p>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="rounded-md bg-green-50 p-4">
          <p className="text-sm font-medium text-green-800">{successMessage}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">{error}</p>
        </div>
      )}

      {/* Profile Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm p-6 space-y-6">
        {/* Avatar Placeholder */}
        <div className="flex items-center space-x-4">
          <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
            {formData.full_name.charAt(0).toUpperCase() || '?'}
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">{formData.full_name || 'Your Name'}</h3>
            <p className="text-sm text-gray-500 capitalize">{user?.role}</p>
          </div>
        </div>

        {/* Full Name */}
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
            Full Name
          </label>
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border ${
              validationErrors.full_name ? 'border-red-300' : 'border-gray-300'
            } shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2`}
          />
          {validationErrors.full_name && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.full_name}</p>
          )}
        </div>

        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border ${
              validationErrors.email ? 'border-red-300' : 'border-gray-300'
            } shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2`}
          />
          {validationErrors.email && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.email}</p>
          )}
        </div>

        {/* Account Info */}
        <div className="border-t pt-6">
          <h3 className="text-sm font-medium text-gray-900 mb-4">Account Information</h3>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-gray-500">Account Type</dt>
              <dd className="mt-1 text-sm font-medium text-gray-900 capitalize">{user?.role}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Member Since</dt>
              <dd className="mt-1 text-sm font-medium text-gray-900">
                {new Date().toLocaleDateString()}
              </dd>
            </div>
          </dl>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end pt-4">
          <button
            type="submit"
            disabled={isSaving || isLoading}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
