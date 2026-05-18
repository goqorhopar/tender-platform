/**
 * TenderDetailPage - View Tender Details
 * Production-grade detail view with actions
 */

import { useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useTenderStore } from '../store/tender.store';
import { useAuthStore } from '../store/auth.store';

export default function TenderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { fetchTenderById, currentTender, isLoading, deleteTender } = useTenderStore();

  useEffect(() => {
    if (id) {
      fetchTenderById(id);
    }
  }, [id]);

  const handleDelete = async () => {
    if (id && window.confirm('Are you sure you want to delete this tender?')) {
      try {
        await deleteTender(id);
        navigate('/tenders');
      } catch (error) {
        console.error('Failed to delete tender:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!currentTender) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-medium text-gray-900">Tender not found</h2>
        <Link to="/tenders" className="mt-4 inline-block text-blue-600 hover:text-blue-500">
          Back to tenders
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link to="/tenders" className="text-sm text-gray-500 hover:text-gray-700">
            ← Back to tenders
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{currentTender.title}</h1>
        </div>
        <div className="flex space-x-3">
          <Link
            to={`/tenders/${currentTender.id}/edit`}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Edit
          </Link>
          <button
            onClick={handleDelete}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Status Badge */}
      <div>
        <span
          className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${
            currentTender.status === 'active'
              ? 'bg-green-100 text-green-800'
              : currentTender.status === 'closed'
              ? 'bg-gray-100 text-gray-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {currentTender.status.charAt(0).toUpperCase() + currentTender.status.slice(1)}
        </span>
      </div>

      {/* Main Content */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Description</h2>
        <p className="text-gray-600 whitespace-pre-wrap">
          {currentTender.description || 'No description provided.'}
        </p>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Budget</h3>
          <p className="text-2xl font-bold text-gray-900">
            ${currentTender.budget?.toLocaleString() || 'Not specified'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Deadline</h3>
          <p className="text-2xl font-bold text-gray-900">
            {new Date(currentTender.deadline).toLocaleDateString(undefined, {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Created By</h3>
          <p className="text-lg font-medium text-gray-900">
            {currentTender.created_by?.full_name || 'Unknown'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Created At</h3>
          <p className="text-lg font-medium text-gray-900">
            {new Date(currentTender.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Requirements */}
      {currentTender.requirements && currentTender.requirements.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Requirements</h2>
          <ul className="list-disc list-inside space-y-2">
            {currentTender.requirements.map((req: string, index: number) => (
              <li key={index} className="text-gray-600">
                {req}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Documents */}
      {currentTender.documents && currentTender.documents.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Documents</h2>
          <div className="space-y-2">
            {currentTender.documents.map((doc: any, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
              >
                <span className="text-sm text-gray-700">{doc.name || `Document ${index + 1}`}</span>
                <a
                  href={doc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-blue-600 hover:text-blue-500"
                >
                  Download
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
