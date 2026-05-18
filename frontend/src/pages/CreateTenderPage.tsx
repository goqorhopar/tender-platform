import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';

const createTenderSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters'),
  description: z.string().min(20, 'Description must be at least 20 characters'),
  initial_price: z.string().min(1, 'Price is required'),
  category: z.string().min(1, 'Category is required'),
  submission_deadline: z.string().min(1, 'Deadline is required'),
});

type CreateTenderForm = z.infer<typeof createTenderSchema>;

export default function CreateTenderPage() {
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateTenderForm>({
    resolver: zodResolver(createTenderSchema),
  });

  const onSubmit = async (data: CreateTenderForm) => {
    // TODO: Implement API call to create tender
    console.log('Creating tender:', data);
    navigate('/tenders');
  };

  return (
    <div>
      <div className="mb-6">
        <a href="/tenders" className="text-sm text-blue-600 hover:text-blue-800">
          ← Back to Tenders
        </a>
      </div>

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h1 className="text-2xl font-bold text-gray-900">Create New Tender</h1>
          <p className="mt-1 text-sm text-gray-500">
            Fill in the details below to create a new tender.
          </p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Title
              </label>
              <input
                type="text"
                id="title"
                {...register('title')}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                rows={4}
                {...register('description')}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="initial_price" className="block text-sm font-medium text-gray-700">
                  Initial Price (RUB)
                </label>
                <input
                  type="number"
                  id="initial_price"
                  {...register('initial_price')}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {errors.initial_price && (
                  <p className="mt-1 text-sm text-red-600">{errors.initial_price.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                  Category
                </label>
                <select
                  id="category"
                  {...register('category')}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="">Select a category</option>
                  <option value="construction">Construction</option>
                  <option value="it">IT Services</option>
                  <option value="consulting">Consulting</option>
                  <option value="supplies">Supplies</option>
                  <option value="other">Other</option>
                </select>
                {errors.category && (
                  <p className="mt-1 text-sm text-red-600">{errors.category.message}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="submission_deadline" className="block text-sm font-medium text-gray-700">
                Submission Deadline
              </label>
              <input
                type="datetime-local"
                id="submission_deadline"
                {...register('submission_deadline')}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              {errors.submission_deadline && (
                <p className="mt-1 text-sm text-red-600">{errors.submission_deadline.message}</p>
              )}
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate('/tenders')}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Creating...' : 'Create Tender'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
