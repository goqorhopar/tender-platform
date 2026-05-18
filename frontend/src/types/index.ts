export interface User {
  id: string;
  email: string;
  full_name?: string;
  phone?: string;
  company_name?: string;
  inn?: string;
  role: 'admin' | 'manager' | 'user' | 'viewer';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface Tender {
  id: string;
  title: string;
  description?: string;
  tender_number: string;
  type: 'government' | 'commercial' | 'international';
  status: 'draft' | 'published' | 'in_progress' | 'completed' | 'cancelled' | 'archived';
  category?: string;
  okpd2_codes?: string[];
  initial_price: number;
  currency: string;
  publication_date?: string;
  submission_deadline?: string;
  review_date?: string;
  customer_name?: string;
  customer_inn?: string;
  customer_region?: string;
  documents_url?: string;
  technical_spec_url?: string;
  ai_summary?: string;
  ai_risk_score?: number;
  ai_recommendations?: Array<{ title: string; description: string }>;
  created_by: string;
  assigned_to_id?: string;
  created_at: string;
  updated_at: string;
}

export interface TenderDocument {
  id: string;
  tender_id: string;
  name: string;
  original_filename: string;
  file_type: 'technical_spec' | 'commercial_proposal' | 'contract' | 'addendum' | 'other';
  mime_type: string;
  file_size: number;
  storage_path: string;
  s3_key?: string;
  uploaded_by_id: string;
  checksum?: string;
  created_at: string;
  updated_at: string;
}

export interface TenderComment {
  id: string;
  tender_id: string;
  user_id: string;
  parent_id?: string;
  content: string;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
  user?: User;
  replies?: TenderComment[];
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  detail?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface TenderFilters extends PaginationParams {
  status?: string;
  type?: string;
  category?: string;
  customer_region?: string;
  min_price?: number;
  max_price?: number;
  search?: string;
}
