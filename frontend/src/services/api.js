/**
 * API Service for connecting to EReceipt Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

/**
 * Get stored auth token
 */
const getToken = () => localStorage.getItem('access_token');

/**
 * Set auth tokens
 */
const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem('access_token', accessToken);
  if (refreshToken) {
    localStorage.setItem('refresh_token', refreshToken);
  }
};

/**
 * Clear auth tokens
 */
const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

/**
 * Make authenticated API request
 */
const apiRequest = async (endpoint, options = {}) => {
  const token = getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  // Handle 401 - Token expired
  if (response.status === 401) {
    // Try to refresh token
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      const refreshed = await refreshAccessToken(refreshToken);
      if (refreshed) {
        // Retry original request with new token
        headers['Authorization'] = `Bearer ${getToken()}`;
        return fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
      }
    }
    // Clear tokens and redirect to login
    clearTokens();
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  
  return response;
};

/**
 * Refresh access token
 */
const refreshAccessToken = async (refreshToken) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`,
      },
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      return true;
    }
    return false;
  } catch {
    return false;
  }
};

// ============================================
// AUTH API
// ============================================

export const authAPI = {
  /**
   * Register new user
   */
  register: async (userData) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    const data = await response.json();
    
    if (response.ok) {
      setTokens(data.access_token, data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    
    return { ok: response.ok, data };
  },
  
  /**
   * Login user
   */
  login: async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    
    if (response.ok) {
      setTokens(data.access_token, data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    
    return { ok: response.ok, data };
  },
  
  /**
   * Logout user
   */
  logout: () => {
    clearTokens();
  },
  
  /**
   * Get current user profile
   */
  getProfile: async () => {
    const response = await apiRequest('/auth/profile');
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Update user profile
   */
  updateProfile: async (profileData) => {
    const response = await apiRequest('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Change password
   */
  changePassword: async (currentPassword, newPassword) => {
    const response = await apiRequest('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => !!getToken(),
  
  /**
   * Get stored user data
   */
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};

// ============================================
// RECEIPTS API
// ============================================

export const receiptsAPI = {
  /**
   * Create new receipt
   */
  create: async (receiptData) => {
    const response = await apiRequest('/receipts', {
      method: 'POST',
      body: JSON.stringify(receiptData),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Get all receipts with pagination
   */
  getAll: async (page = 1, perPage = 20, search = '', status = '') => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    
    const response = await apiRequest(`/receipts?${params}`);
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Get single receipt by ID
   */
  getById: async (id) => {
    const response = await apiRequest(`/receipts/${id}`);
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Update receipt
   */
  update: async (id, receiptData) => {
    const response = await apiRequest(`/receipts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(receiptData),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Delete receipt
   */
  delete: async (id) => {
    const response = await apiRequest(`/receipts/${id}`, {
      method: 'DELETE',
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Get receipt statistics
   */
  getStats: async () => {
    const response = await apiRequest('/receipts/stats');
    return { ok: response.ok, data: await response.json() };
  },
};

// ============================================
// NOTIFICATIONS API
// ============================================

export const notificationsAPI = {
  /**
   * Send receipt via email
   */
  sendEmail: async (receiptId, email = null) => {
    const body = email ? { email } : {};
    const response = await apiRequest(`/notifications/send-email/${receiptId}`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Send receipt via SMS
   */
  sendSMS: async (receiptId, phone = null) => {
    const body = phone ? { phone } : {};
    const response = await apiRequest(`/notifications/send-sms/${receiptId}`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Send receipt via both email and SMS
   */
  sendBoth: async (receiptId, email = null, phone = null) => {
    const body = {};
    if (email) body.email = email;
    if (phone) body.phone = phone;
    
    const response = await apiRequest(`/notifications/send-both/${receiptId}`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Test email configuration
   */
  testEmail: async (email) => {
    const response = await apiRequest('/notifications/test-email', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Test SMS configuration
   */
  testSMS: async (phone) => {
    const response = await apiRequest('/notifications/test-sms', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    });
    return { ok: response.ok, data: await response.json() };
  },
  
  /**
   * Get notification service configuration status
   */
  getConfig: async () => {
    const response = await apiRequest('/notifications/config');
    return { ok: response.ok, data: await response.json() };
  },
};

export default {
  auth: authAPI,
  receipts: receiptsAPI,
  notifications: notificationsAPI,
};

