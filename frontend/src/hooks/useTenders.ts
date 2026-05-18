/**
 * useTenders Hook - Tender State Management
 * Production-grade hook for tender operations
 */

import { useCallback } from 'react';
import { useTenderStore } from '../store/tender.store';
import type { CreateTenderRequest, UpdateTenderRequest } from '../services/tender.service';

export function useTenders() {
  const {
    tenders,
    currentTender,
    isLoading,
    error,
    totalPages,
    currentPage,
    fetchTenders,
    fetchTenderById,
    createTender,
    updateTender,
    deleteTender,
    clearError,
    setCurrentTender,
  } = useTenderStore();

  const loadTenders = useCallback(
    async (page?: number, limit?: number) => {
      await fetchTenders(page, limit);
    },
    [fetchTenders]
  );

  const loadTender = useCallback(
    async (id: string) => {
      await fetchTenderById(id);
    },
    [fetchTenderById]
  );

  const createNewTender = useCallback(
    async (data: CreateTenderRequest) => {
      return await createTender(data);
    },
    [createTender]
  );

  const updateExistingTender = useCallback(
    async (id: string, data: UpdateTenderRequest) => {
      return await updateTender(id, data);
    },
    [updateTender]
  );

  const removeTender = useCallback(
    async (id: string) => {
      await deleteTender(id);
    },
    [deleteTender]
  );

  return {
    tenders,
    currentTender,
    isLoading,
    error,
    totalPages,
    currentPage,
    loadTenders,
    loadTender,
    createTender: createNewTender,
    updateTender: updateExistingTender,
    deleteTender: removeTender,
    clearError,
    setCurrentTender,
  };
}

export default useTenders;
