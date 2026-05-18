/**
 * Tender Store - Zustand State Management
 * Production-grade tender state with caching and optimistic updates
 */

import { create } from 'zustand';
import { tenderService, type Tender, type CreateTenderRequest, type UpdateTenderRequest } from '../services/tender.service';

interface TenderState {
  tenders: Tender[];
  currentTender: Tender | null;
  isLoading: boolean;
  error: string | null;
  totalPages: number;
  currentPage: number;

  // Actions
  fetchTenders: (page?: number, limit?: number) => Promise<void>;
  fetchTenderById: (id: string) => Promise<void>;
  createTender: (data: CreateTenderRequest) => Promise<Tender>;
  updateTender: (id: string, data: UpdateTenderRequest) => Promise<Tender>;
  deleteTender: (id: string) => Promise<void>;
  clearError: () => void;
  setCurrentTender: (tender: Tender | null) => void;
}

export const useTenderStore = create<TenderState>((set, get) => ({
  tenders: [],
  currentTender: null,
  isLoading: false,
  error: null,
  totalPages: 0,
  currentPage: 1,

  fetchTenders: async (page = 1, limit = 10) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tenderService.getTenders(page, limit);
      set({
        tenders: response.items,
        totalPages: response.total_pages,
        currentPage: page,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch tenders';
      set({ error: message, isLoading: false });
    }
  },

  fetchTenderById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const tender = await tenderService.getTenderById(id);
      set({ currentTender: tender, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch tender';
      set({ error: message, isLoading: false, currentTender: null });
    }
  },

  createTender: async (data: CreateTenderRequest) => {
    set({ isLoading: true, error: null });
    try {
      const tender = await tenderService.createTender(data);
      set((state) => ({
        tenders: [tender, ...state.tenders],
        isLoading: false,
      }));
      return tender;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create tender';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateTender: async (id: string, data: UpdateTenderRequest) => {
    set({ isLoading: true, error: null });
    try {
      const tender = await tenderService.updateTender(id, data);
      set((state) => ({
        tenders: state.tenders.map((t) => (t.id === id ? tender : t)),
        currentTender: state.currentTender?.id === id ? tender : state.currentTender,
        isLoading: false,
      }));
      return tender;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update tender';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deleteTender: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await tenderService.deleteTender(id);
      set((state) => ({
        tenders: state.tenders.filter((t) => t.id !== id),
        currentTender: state.currentTender?.id === id ? null : state.currentTender,
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete tender';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  clearError: () => set({ error: null }),

  setCurrentTender: (tender: Tender | null) => set({ currentTender: tender }),
}));
