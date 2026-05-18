import apiClient from './api';
import type { Tender, TenderFilters, PaginatedResponse, TenderDocument, TenderComment } from '../types';

export const tenderService = {
  async getTenders(filters?: TenderFilters): Promise<PaginatedResponse<Tender>> {
    const response = await apiClient.get<PaginatedResponse<Tender>>('/tenders', { params: filters });
    return response.data;
  },

  async getTenderById(id: string): Promise<Tender> {
    const response = await apiClient.get<Tender>(`/tenders/${id}`);
    return response.data;
  },

  async createTender(data: Partial<Tender>): Promise<Tender> {
    const response = await apiClient.post<Tender>('/tenders', data);
    return response.data;
  },

  async updateTender(id: string, data: Partial<Tender>): Promise<Tender> {
    const response = await apiClient.put<Tender>(`/tenders/${id}`, data);
    return response.data;
  },

  async deleteTender(id: string): Promise<void> {
    await apiClient.delete(`/tenders/${id}`);
  },

  async getDocuments(tenderId: string): Promise<TenderDocument[]> {
    const response = await apiClient.get<TenderDocument[]>(`/tenders/${tenderId}/documents`);
    return response.data;
  },

  async uploadDocument(tenderId: string, file: File): Promise<TenderDocument> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<TenderDocument>(
      `/tenders/${tenderId}/documents`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  async getComments(tenderId: string): Promise<TenderComment[]> {
    const response = await apiClient.get<TenderComment[]>(`/tenders/${tenderId}/comments`);
    return response.data;
  },

  async addComment(tenderId: string, content: string, parentId?: string): Promise<TenderComment> {
    const response = await apiClient.post<TenderComment>(`/tenders/${tenderId}/comments`, {
      content,
      parent_id: parentId,
    });
    return response.data;
  },

  async searchTenders(query: string, filters?: TenderFilters): Promise<PaginatedResponse<Tender>> {
    const response = await apiClient.get<PaginatedResponse<Tender>>('/tenders/search', {
      params: { q: query, ...filters },
    });
    return response.data;
  },
};
