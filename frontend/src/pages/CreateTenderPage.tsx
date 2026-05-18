/**
 * CreateTenderPage - Create New Tender
 * Production-grade form with validation
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTenderStore } from '../store/tender.store';
import type { CreateTenderRequest } from '../services/tender.service';

export default function CreateTenderPage() {
  const navigate = useNavigate();
  const { createTender, isLoading, error, clearError } = useTenderStore();
  
  const [formData, setFormData] = useState<CreateTenderRequest>({
    title: '',
    description: '',
    budget: undefined,
    deadline: '',
    requirements: [],
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [requirementInput, setRequirementInput] = useState('');

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.title) {
      errors.title = 'Title is required';
    } else if (formData.title.length < 5) {
      errors.title = 'Title must be at least 5 characters';
    }
    
    if (!formData.description) {
      errors.description = 'Description is required';
    } else if (formData.description.length < 20) {
      errors.description = 'Description must be at least 20 characters';
    }
    
    if (!formData.budget || formData.budget <= 0) {
      errors.budget = 'Budget must be greater than 0';
    }
    
    if (!formData.deadline) {
      errors.deadline = 'Deadline is required';
    } else if (new Date(formData.deadline) <= new Date()) {
      errors.deadline = 'Deadline must be in the future';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (!validateForm()) return;
    
    try {
      await createTender(formData);
      navigate('/tenders');
    } catch {
      // Error handled by store
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (validationErrors[name]) {
      setValidationErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleAddRequirement = () => {
    if (requirementInput.trim()) {
      setFormData((prev) => ({
        ...prev,
        requirements: [...(prev.requirements || []), requirementInput.trim()],
      }));
      setRequirementInput('');
    }
  };

  const handleRemoveRequirement = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      requirements: prev.requirements?.filter((_, i) => i !== index),
    }));
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link to="/tenders" className="text-sm text-gray-500 hover:text-gray-700">
            ← Back to tenders
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">Create New Tender</h1>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm font-medium text-red-800">{error}</p>
          </div>
        )}

        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border ${
              validationErrors.title ? 'border-red-300' : 'border-gray-300'
            } shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2`}
            placeholder="Enter tender title"
          />
          {validationErrors.title && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.title}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description *
          </label>
          <textarea
            id="description"
            name="description"
            rows={4}
            value={formData.description}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border ${
              validationErrors.description ? 'border-red-300' : 'border-gray-300'
            } shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2`}
            placeholder="Describe the tender details..."
          />
          {validationErrors.description && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.description}</p>
          )}
        </div>

        {/* Budget and Deadline */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="budget" className="block text-sm font-medium text-gray-700">
              Budget ($) *
            </label>
            <input
              type="number"
              id="budget"
              name="budget"
              value={formData.budget || ''}
              onChange={handleChange}
              min="0"
              step="0.01"
              className={`mt-1 block w-full rounded-md border ${
                validationErrors.budget ? 'border-red-300' : 'border-gray-300'
              } shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2`}
              placeholder="10000"
            />
            {validationErrors.budget && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.budget}</p>
            )}
          </div>

          <div>
            <label htmlFor="deadline" className="block text-sm font-medium text-gray-700">
              Deadline *
            </label>
            <input
              type="date"
              id="deadline"
              name="deadline"
              value={formData.deadline}
              onChange={handleChange}
              min={new Date().toISOString().split('T')[0]}
              className={`mt-1 block w-full rounded-md border ${
                validationErrors.deadline ? 'border-red-300' : 'border-gray-300'
              } shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2`}
            />
            {validationErrors.deadline && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.deadline}</p>
            )}
          </div>
        </div>

        {/* Requirements */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Requirements</label>
          <div className="mt-1 flex space-x-2">
            <input
              type="text"
              value={requirementInput}
              onChange={(e) => setRequirementInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddRequirement())}
              className="flex-1 block w-full rounded-md border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2"
              placeholder="Add a requirement"
            />
            <button
              type="button"
              onClick={handleAddRequirement}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Add
            </button>
          </div>
          
          {formData.requirements && formData.requirements.length > 0 && (
            <ul className="mt-3 space-y-2">
              {formData.requirements.map((req, index) => (
                <li
                  key={index}
                  className="flex items-center justify-between bg-gray-50 rounded-md px-3 py-2"
                >
                  <span className="text-sm text-gray-700">{req}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveRequirement(index)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-3 pt-6 border-t">
          <Link
            to="/tenders"
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Creating...
              </>
            ) : (
              'Create Tender'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
