import apiClient from './api';
import type { User, LoginRequest, RegisterRequest, AuthTokens } from '../types';

export interface LoginResponse extends AuthTokens {
  user: User;
}

export interface RegisterResponse extends AuthTokens {
  user: User;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const params = new URLSearchParams();
    params.append('username', credentials.username);
    params.append('password', credentials.password);

    const response = await apiClient.post<AuthTokens>('/auth/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Get current user after login
    const userResponse = await apiClient.get<User>('/users/me');
    
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);

    return {
      ...response.data,
      user: userResponse.data,
    };
  },

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await apiClient.post<User>('/auth/register', data);
    
    // Auto-login after registration
    const loginParams = new URLSearchParams();
    loginParams.append('username', data.email);
    loginParams.append('password', data.password);
    
    const tokenResponse = await apiClient.post<AuthTokens>('/auth/token', loginParams, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    localStorage.setItem('access_token', tokenResponse.data.access_token);
    localStorage.setItem('refresh_token', tokenResponse.data.refresh_token);

    return {
      ...tokenResponse.data,
      user: response.data,
    };
  },

  async logout(): Promise<void> {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    const response = await apiClient.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    // Get current user after refresh
    const userResponse = await apiClient.get<User>('/users/me');

    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);

    return {
      ...response.data,
      user: userResponse.data,
    };
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};
