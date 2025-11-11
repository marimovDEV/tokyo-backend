// API configuration and types
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api';

export interface MenuItem {
  id: number;
  name: string;
  name_uz: string;
  name_ru: string;
  description: string;
  description_uz: string;
  description_ru: string;
  price: number;
  image?: string;
  category: number;
  category_name: string;
  category_name_uz: string;
  category_name_ru: string;
  available: boolean;
  prep_time?: string;
  rating?: number;
  ingredients: string[];
  ingredients_uz: string[];
  ingredients_ru: string[];
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  name_uz: string;
  name_ru: string;
  icon: string;
  image?: string;
  created_at: string;
  updated_at: string;
}


export interface Order {
  id: number;
  table_number: number;
  customer_name?: string;
  total: number;
  status: "pending" | "preparing" | "ready" | "served" | "cancelled";
  notes?: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface OrderItem {
  id: number;
  menu_item: number;
  menu_item_name: string;
  menu_item_name_uz: string;
  menu_item_name_ru: string;
  quantity: number;
  notes?: string;
  price: number;
  total_price: number;
}

export interface CartItem {
  id: number;
  menu_item: number;
  menu_item_name: string;
  menu_item_name_uz: string;
  menu_item_name_ru: string;
  menu_item_image?: string;
  menu_item_price: number;
  quantity: number;
  notes?: string;
  price: number;
  total_price: number;
  created_at: string;
  updated_at: string;
}

export interface Cart {
  id: number;
  session_key: string;
  table_number?: number;
  customer_name?: string;
  notes?: string;
  total_items: number;
  total_price: number;
  items: CartItem[];
  created_at: string;
  updated_at: string;
}

export interface Promotion {
  id: number;
  title: string;
  title_uz: string;
  title_ru: string;
  description: string;
  description_uz: string;
  description_ru: string;
  image?: string;
  active: boolean;
  link?: string;
  category?: number;
  category_name?: string;
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: number;
  name: string;
  surname: string;
  comment: string;
  rating: number;
  date: string;
  approved: boolean;
  deleted: boolean;
}

export interface SiteSettings {
  id: number;
  site_name: string;
  site_name_uz: string;
  site_name_ru: string;
  logo?: string;
  favicon?: string;
  phone: string;
  email: string;
  address: string;
  address_uz: string;
  address_ru: string;
  working_hours: string;
  working_hours_uz: string;
  working_hours_ru: string;
  facebook_url?: string;
  instagram_url?: string;
  telegram_url?: string;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  is_maintenance_mode: boolean;
  maintenance_message?: string;
  created_at: string;
  updated_at: string;
}

export interface TextContent {
  id: number;
  content_type: string;
  key: string;
  title?: string;
  subtitle?: string;
  description?: string;
  content?: string;
  title_uz?: string;
  subtitle_uz?: string;
  description_uz?: string;
  content_uz?: string;
  title_ru?: string;
  subtitle_ru?: string;
  description_ru?: string;
  content_ru?: string;
  button_text?: string;
  button_text_uz?: string;
  button_text_ru?: string;
  is_active: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface RestaurantInfo {
  id: number;
  restaurant_name: string;
  restaurant_name_uz: string;
  restaurant_name_ru: string;
  about_title: string;
  about_title_uz: string;
  about_title_ru: string;
  about_description_1: string;
  about_description_1_uz: string;
  about_description_1_ru: string;
  about_description_2: string;
  about_description_2_uz: string;
  about_description_2_ru: string;
  hero_title: string;
  hero_subtitle: string;
  hero_subtitle_uz: string;
  hero_subtitle_ru: string;
  view_menu_button: string;
  view_menu_button_uz: string;
  view_menu_button_ru: string;
  go_to_menu_button: string;
  go_to_menu_button_uz: string;
  go_to_menu_button_ru: string;
  reviews_title: string;
  reviews_title_uz: string;
  reviews_title_ru: string;
  leave_review_title: string;
  leave_review_title_uz: string;
  leave_review_title_ru: string;
  first_name_label: string;
  first_name_label_uz: string;
  first_name_label_ru: string;
  last_name_label: string;
  last_name_label_uz: string;
  last_name_label_ru: string;
  comment_label: string;
  comment_label_uz: string;
  comment_label_ru: string;
  rate_us_label: string;
  rate_us_label_uz: string;
  rate_us_label_ru: string;
  submit_button: string;
  submit_button_uz: string;
  submit_button_ru: string;
  no_reviews_text: string;
  no_reviews_text_uz: string;
  no_reviews_text_ru: string;
  hero_image?: string;
  about_image?: string;
  created_at: string;
  updated_at: string;
}

// API functions
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async getCsrfToken(): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/csrf/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        return data.csrfToken;
      }
    } catch (error) {
      console.warn('Failed to get CSRF token:', error);
    }
    return '';
  }

  private async request<T>(endpoint: string, options: RequestInit = {}, parseJson: boolean = true, retries: number = 2): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Get CSRF token for POST/PUT/DELETE requests
    let csrfToken = '';
    if (options.method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method.toUpperCase())) {
      csrfToken = await this.getCsrfToken();
    }
    
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      const response = await fetch(url, {
        headers: {
          // Only set Content-Type for JSON requests, not for FormData
          // For FormData, let browser set multipart/form-data with boundary
          ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
          ...(csrfToken && { 'X-CSRFToken': csrfToken }),
          ...options.headers,
        },
        credentials: 'include', // Include cookies for session management
        signal: controller.signal,
        ...options,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = `API request failed: ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.text();
          if (errorData) {
            errorMessage += ` - ${errorData}`;
          }
        } catch (e) {
          // Ignore parsing errors for error message
        }
        
        // Retry for server errors (5xx) or network issues
        if (retries > 0 && (response.status >= 500 || response.status === 0)) {
          console.warn(`Retrying request to ${endpoint}, attempts left: ${retries}`);
          await new Promise(resolve => setTimeout(resolve, 1000 * (3 - retries))); // Exponential backoff
          return this.request<T>(endpoint, options, parseJson, retries - 1);
        }
        
        throw new Error(errorMessage);
      }

      // Don't try to parse JSON for DELETE requests that return 204 No Content
      if (!parseJson || response.status === 204) {
        return undefined as T;
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      // Retry for network errors or timeouts
      if (retries > 0 && (error.name === 'AbortError' || error.name === 'TypeError')) {
        console.warn(`Retrying request to ${endpoint}, attempts left: ${retries}`);
        await new Promise(resolve => setTimeout(resolve, 1000 * (3 - retries))); // Exponential backoff
        return this.request<T>(endpoint, options, parseJson, retries - 1);
      }
      
      throw error;
    }
  }

  // Categories
  async getCategories(): Promise<Category[]> {
    const response = await this.request<{results: Category[]}>('/categories/');
    return response.results;
  }

  async getCategory(id: number): Promise<Category> {
    return this.request<Category>(`/categories/${id}/`);
  }

  async createCategory(category: Omit<Category, 'id' | 'created_at' | 'updated_at'> & { imageFile?: File }): Promise<Category> {
    const formData = new FormData();
    
    // Add all text fields
    Object.entries(category).forEach(([key, value]) => {
      if (key === 'imageFile') return; // Skip the file, we'll handle it separately
      if (key === 'image' && !value) return; // Skip empty image field
      if (value !== null && value !== undefined) {
        formData.append(key, value.toString());
      }
    });
    
    // Add image file if provided
    if (category.imageFile) {
      formData.append('image', category.imageFile);
    }
    
    return this.request<Category>('/categories/', {
      method: 'POST',
      body: formData,
    });
  }

  async updateCategory(id: number, category: Partial<Omit<Category, 'id' | 'created_at' | 'updated_at'>> & { imageFile?: File }): Promise<Category> {
    const formData = new FormData();
    
    // Add all text fields
    Object.entries(category).forEach(([key, value]) => {
      if (key === 'imageFile') return; // Skip the file, we'll handle it separately
      if (key === 'image' && !value) return; // Skip empty image field
      if (value !== null && value !== undefined) {
        formData.append(key, value.toString());
      }
    });
    
    // Add image file if provided
    if (category.imageFile) {
      formData.append('image', category.imageFile);
    }
    
    return this.request<Category>(`/categories/${id}/`, {
      method: 'PATCH',
      body: formData,
    });
  }

  async deleteCategory(id: number): Promise<void> {
    await this.request<void>(`/categories/${id}/`, {
      method: 'DELETE',
    });
  }

  // Menu Items
  async getMenuItems(): Promise<MenuItem[]> {
    const response = await this.request<any>('/menu-items/?show_all=true');
    return Array.isArray(response) ? response : (response.results || []);
  }

  async getMenuItem(id: number): Promise<MenuItem> {
    return this.request<MenuItem>(`/menu-items/${id}/`);
  }

  async createMenuItem(menuItem: Omit<MenuItem, 'id' | 'created_at' | 'updated_at' | 'category_name' | 'category_name_uz' | 'category_name_ru'> & { imageFile?: File }): Promise<MenuItem> {
    const formData = new FormData();
    
    // Add all text fields
    Object.entries(menuItem).forEach(([key, value]) => {
      if (key === 'imageFile') return; // Skip the file, we'll handle it separately
      if (key === 'image' && !value) return; // Skip empty image field
      if (Array.isArray(value)) {
        formData.append(key, JSON.stringify(value));
      } else if (value !== null && value !== undefined) {
        formData.append(key, value.toString());
      }
    });
    
    // Add image file if provided
    if (menuItem.imageFile) {
      formData.append('image', menuItem.imageFile);
    }
    
    return this.request<MenuItem>('/menu-items/', {
      method: 'POST',
      body: formData,
    });
  }

  async updateMenuItem(id: number, menuItem: Partial<Omit<MenuItem, 'id' | 'created_at' | 'updated_at' | 'category_name' | 'category_name_uz' | 'category_name_ru'>> & { imageFile?: File }): Promise<MenuItem> {
    const formData = new FormData();
    
    // Add all text fields
    Object.entries(menuItem).forEach(([key, value]) => {
      if (key === 'imageFile') return; // Skip the file, we'll handle it separately
      if (key === 'image' && !value) return; // Skip empty image field
      if (Array.isArray(value)) {
        formData.append(key, JSON.stringify(value));
      } else if (value !== null && value !== undefined) {
        formData.append(key, value.toString());
      }
    });
    
    // Add image file if provided
    if (menuItem.imageFile) {
      formData.append('image', menuItem.imageFile);
    }
    
    return this.request<MenuItem>(`/menu-items/${id}/`, {
      method: 'PATCH',
      body: formData,
    });
  }

  async deleteMenuItem(id: number): Promise<void> {
    await this.request<void>(`/menu-items/${id}/`, {
      method: 'DELETE',
    });
  }

  async getMenuItemsByCategory(categoryId: number): Promise<MenuItem[]> {
    const response = await this.request<{results: MenuItem[]}>(`/categories/${categoryId}/menu-items/`);
    return response.results;
  }

  async searchMenuItems(query: string, categoryId?: number): Promise<MenuItem[]> {
    const params = new URLSearchParams({ q: query });
    if (categoryId) {
      params.append('category', categoryId.toString());
    }
    return this.request<MenuItem[]>(`/search/?${params}`);
  }

  // Promotions
  async getPromotions(): Promise<Promotion[]> {
    const response = await this.request<{results: Promotion[]}>('/promotions/');
    return response.results;
  }

  async getPromotion(id: number): Promise<Promotion> {
    return this.request<Promotion>(`/promotions/${id}/`);
  }

  async createPromotion(promotion: Omit<Promotion, 'id' | 'created_at' | 'updated_at' | 'category_name'> & { imageFile?: File }): Promise<Promotion> {
    const formData = new FormData();
    
    // Add all text fields
    Object.entries(promotion).forEach(([key, value]) => {
      if (key === 'imageFile') return; // Skip the file, we'll handle it separately
      if (key === 'image' && !value) return; // Skip empty image field
      if (value !== null && value !== undefined) {
        formData.append(key, value.toString());
      }
    });
    
    // Add image file if provided
    if (promotion.imageFile) {
      formData.append('image', promotion.imageFile);
    }
    
    return this.request<Promotion>('/promotions/', {
      method: 'POST',
      body: formData,
    });
  }

  async updatePromotion(id: number, promotion: Partial<Omit<Promotion, 'id' | 'created_at' | 'updated_at' | 'category_name'>> & { imageFile?: File }): Promise<Promotion> {
    const formData = new FormData();
    
    // Add all text fields
    Object.entries(promotion).forEach(([key, value]) => {
      if (key === 'imageFile') return; // Skip the file, we'll handle it separately
      if (key === 'image' && !value) return; // Skip empty image field
      if (value !== null && value !== undefined) {
        formData.append(key, value.toString());
      }
    });
    
    // Add image file if provided
    if (promotion.imageFile) {
      formData.append('image', promotion.imageFile);
    }
    
    return this.request<Promotion>(`/promotions/${id}/`, {
      method: 'PATCH',
      body: formData,
    });
  }

  async deletePromotion(id: number): Promise<void> {
    await this.request<void>(`/promotions/${id}/`, {
      method: 'DELETE',
    });
  }

  // Reviews
  async getReviews(): Promise<Review[]> {
    const response = await this.request<{results: Review[]}>('/reviews/');
    return response.results;
  }

  async getAllReviews(): Promise<Review[]> {
    const response = await this.request<{results: Review[]}>('/admin/reviews/');
    return response.results;
  }

  async getAllFeedbacks(): Promise<Feedback[]> {
    console.log('API Base URL:', this.baseUrl);
    console.log('Making request to:', `${this.baseUrl}/feedback/`);
    const response = await this.request<{results: Feedback[]}>('/feedback/');
    console.log('API Response:', response);
    return response.results;
  }

  async createFeedback(feedback: Omit<Feedback, 'id' | 'created_at' | 'updated_at'>): Promise<Feedback> {
    return this.request<Feedback>('/feedback/', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  async deleteFeedback(id: number): Promise<void> {
    return this.request<void>(`/feedback/${id}/`, {
      method: 'DELETE',
    });
  }

  async createReview(review: Omit<Review, 'id' | 'date' | 'approved'>): Promise<Review> {
    return this.request<Review>('/reviews/', {
      method: 'POST',
      body: JSON.stringify(review),
    });
  }

  async updateReview(id: number, data: Partial<Review>): Promise<Review> {
    return this.request<Review>(`/reviews/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteReview(id: number): Promise<void> {
    await this.request<void>(`/reviews/${id}/`, {
      method: 'DELETE',
    }, false); // Don't try to parse JSON for DELETE requests
  }

  // Review Actions
  async getReviewActions(): Promise<any[]> {
    const response = await this.request<{results: any[]}>('/admin/review-actions/');
    return response.results;
  }

  async deleteReviewAction(id: number): Promise<void> {
    await this.request<void>(`/admin/review-actions/${id}/`, {
      method: 'DELETE',
    }, false);
  }

  // Cart Management
  async getAllCarts(): Promise<any[]> {
    const response = await this.request<any[]>('/admin/carts/');
    return response;
  }

  async clearCart(cartId?: number): Promise<void> {
    const url = cartId ? `/admin/carts/${cartId}/` : '/admin/carts/';
    await this.request<void>(url, {
      method: 'DELETE',
    }, false);
  }

  // Orders
  async getOrders(): Promise<Order[]> {
    const response = await this.request<{results: Order[]}>('/orders/');
    return response.results;
  }

  async getOrder(id: number): Promise<Order> {
    return this.request<Order>(`/orders/${id}/`);
  }

  async createOrder(order: {
    table_number: number;
    customer_name?: string;
    notes?: string;
    items: {
      menu_item: number;
      quantity: number;
      notes?: string;
    }[];
  }): Promise<Order> {
    return this.request<Order>('/orders/', {
      method: 'POST',
      body: JSON.stringify(order),
    });
  }

  async updateOrderStatus(id: number, status: Order['status']): Promise<Order> {
    return this.request<Order>(`/orders/${id}/status/`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  // Stats
  async getStats(): Promise<{
    total_categories: number;
    total_menu_items: number;
    available_menu_items: number;
    total_promotions: number;
    total_reviews: number;
    average_rating: number;
  }> {
    return this.request('/stats/');
  }

  // Site Settings
  async getSiteSettings(): Promise<SiteSettings> {
    return this.request<SiteSettings>('/site-settings/');
  }

  // Text Content
  async getTextContent(): Promise<TextContent[]> {
    const response = await this.request<{results: TextContent[]}>('/text-content/');
    return response.results;
  }

  async getTextContentByType(contentType: string): Promise<TextContent[]> {
    const response = await this.request<{results: TextContent[]}>(`/text-content/type/${contentType}/`);
    return response.results;
  }

  // Restaurant Info
  async getRestaurantInfo(): Promise<RestaurantInfo> {
    return this.request<RestaurantInfo>('/restaurant-info/');
  }

  // Cart
  async getCart(): Promise<Cart> {
    try {
      const response = await this.request<Cart>('/cart/');
      return response;
    } catch (error) {
      console.error('Error fetching cart:', error);
      // If cart not found, return empty cart
      if (error.message && error.message.includes('404')) {
        return {
          id: 0,
          session_key: '',
          table_number: null,
          customer_name: null,
          notes: null,
          total_items: 0,
          total_price: 0,
          items: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
      }
      throw error;
    }
  }

  async addToCart(data: {
    menu_item_id: number;
    quantity: number;
    notes?: string;
  }): Promise<Cart> {
    return this.request<Cart>('/cart/add/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCartItem(itemId: number, data: {
    quantity?: number;
    notes?: string;
  }): Promise<Cart> {
    try {
      return await this.request<Cart>(`/cart/items/${itemId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.error(`Error updating cart item ${itemId}:`, error);
      throw error;
    }
  }

  async removeFromCart(itemId: number): Promise<Cart> {
    try {
      return await this.request<Cart>(`/cart/items/${itemId}/`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error(`Error removing cart item ${itemId}:`, error);
      throw error;
    }
  }

  async clearCart(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/cart/', {
      method: 'DELETE',
    });
  }

  async createOrderFromCart(data: {
    table_number: number;
    customer_name?: string;
    notes?: string;
  }): Promise<Order> {
    return this.request<Order>('/cart/order/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Create a default API client instance
export const apiClient = new ApiClient();

// Utility functions for formatting
export const formatPrice = (price: number): string => {
  // Convert to integer to remove decimal places
  const integerPrice = Math.round(price);
  return `${integerPrice.toLocaleString("uz-UZ")} so'm`;
};

export const formatWeight = (weight: number): string => {
  // Convert to integer to remove decimal places and add gram symbol
  const integerWeight = Math.round(weight);
  return `${integerWeight}г`;
};

// Utility function to get full image URL
export const getImageUrl = (imagePath: string | null | undefined): string => {
  if (!imagePath) return '/placeholder.svg';
  
  // If it's already a full URL, return as is
  if (imagePath.startsWith('http')) {
    return imagePath;
  }
  
  // For production, always use the correct backend URL
  const backendUrl = 'https://api.tokyokafe.uz';
  
  // Ensure imagePath starts with /
  if (!imagePath.startsWith('/')) {
    imagePath = '/' + imagePath;
  }
  
  // Special handling for logo.png - try backend first, then fallback to Vercel
  if (imagePath === '/logo.png') {
    return `${backendUrl}/static/logo.png`;
  }
  
  const fullUrl = `${backendUrl}${imagePath}`;
  console.log('Image URL constructed:', fullUrl);
  return fullUrl;
};

// Local storage helpers for cart (frontend only)
export const getStoredCart = (): CartItem[] => {
  if (typeof window === "undefined") return [];
  const stored = localStorage.getItem("restaurant-cart");
  return stored ? JSON.parse(stored) : [];
};

export const saveCart = (cart: CartItem[]) => {
  if (typeof window === "undefined") return;
  localStorage.setItem("restaurant-cart", JSON.stringify(cart));
};

// Clear all session data (useful for debugging cart issues)
export const clearSessionData = () => {
  if (typeof window === "undefined") return;
  
  // Clear localStorage
  localStorage.removeItem("restaurant-cart");
  localStorage.removeItem("restaurant-language");
  
  // Clear sessionStorage
  sessionStorage.clear();
  
  console.log("Session data cleared - page will refresh to get new session");
  
  // Refresh page to get new session
  window.location.reload();
};

export const clearCart = () => {
  if (typeof window === "undefined") return;
  localStorage.removeItem("restaurant-cart");
};

// Order management functions
export const getStoredOrders = (): Order[] => {
  if (typeof window === "undefined") return [];
  const stored = localStorage.getItem("restaurant-orders");
  return stored ? JSON.parse(stored) : [];
};

export const saveOrder = (order: Order) => {
  if (typeof window === "undefined") return;
  const orders = getStoredOrders();
  orders.push(order);
  localStorage.setItem("restaurant-orders", JSON.stringify(orders));
};
