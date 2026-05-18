import React from 'react';
import { useParams } from 'react-router-dom';

export default function TenderDetailPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <div className="mb-6">
        <a href="/tenders" className="text-sm text-blue-600 hover:text-blue-800">
          ← Back to Tenders
        </a>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h1 className="text-2xl font-bold text-gray-900">Tender Details</h1>
          <p className="mt-1 text-sm text-gray-500">ID: {id}</p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <div className="px-4 py-12 sm:px-6 lg:px-8">
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Tender not found</h3>
              <p className="mt-1 text-sm text-gray-500">
                This tender does not exist or has been removed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
