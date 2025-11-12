"use client"

import { useCSRF } from './use-csrf';
import { useState, useEffect, useCallback, useMemo } from 'react';

// API client hook - CSRF token bilan avtomatik ishlaydi
export function useApiClient() {
  const { makeAuthenticatedRequest, getCSRFHeaders, isLoading: csrfLoading } = useCSRF();

  const apiClient = useMemo(() => ({
    // GET so'rovlar
    async get<T>(endpoint: string): Promise<T> {
      // Cache-busting uchun timestamp qo'shish
      const timestamp = new Date().getTime();
      const random = Math.random().toString(36).substring(7);
      const random2 = Math.random().toString(36).substring(7);
      const random3 = Math.random().toString(36).substring(7);
      const separator = endpoint.includes('?') ? '&' : '?';
      const url = `${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}${endpoint}${separator}t=${timestamp}&r=${random}&r2=${random2}&r3=${random3}`;
      
      // Retry mechanism for network errors
      let lastError;
      for (let attempt = 1; attempt <= 3; attempt++) {
        try {
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            cache: 'no-cache', // Cache-ni to'liq o'chirish
            signal: AbortSignal.timeout(10000), // 10 second timeout
          });
          
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
          }
          
          const data = await response.json();
          return data;
        } catch (error) {
          lastError = error;
          
          // Don't retry on client errors (4xx) or server errors (5xx)
          if (error.message && (error.message.includes('400') || error.message.includes('401') || 
              error.message.includes('403') || error.message.includes('404') || 
              error.message.includes('500'))) {
            throw error;
          }
          
          // Wait before retry (exponential backoff)
          if (attempt < 3) {
            await new Promise(resolve => setTimeout(resolve, attempt * 1000));
          }
        }
      }
      
      throw lastError;
    },

    // POST so'rovlar
    async post<T>(endpoint: string, data: any): Promise<T> {
      const response = await makeAuthenticatedRequest(
        `${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}${endpoint}`,
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      return response.json();
    },

    // PUT so'rovlar
    async put<T>(endpoint: string, data: any): Promise<T> {
      const response = await makeAuthenticatedRequest(
        `${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}${endpoint}`,
        {
          method: 'PUT',
          body: JSON.stringify(data),
        }
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      return response.json();
    },

    // PATCH so'rovlar
    async patch<T>(endpoint: string, data: any): Promise<T> {
      const response = await makeAuthenticatedRequest(
        `${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}${endpoint}`,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      return response.json();
    },

    // DELETE so'rovlar
    async delete(endpoint: string): Promise<void> {
      const response = await makeAuthenticatedRequest(
        `${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}${endpoint}`,
        {
          method: 'DELETE',
        }
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
    },

    // FormData bilan so'rovlar (fayl yuklash uchun)
    async postFormData<T>(endpoint: string, formData: FormData): Promise<T> {
      const response = await makeAuthenticatedRequest(
        `${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}${endpoint}`,
        {
          method: 'POST',
          body: formData,
          // Content-Type ni qo'lda o'rnatmaymiz - brauzer o'zi multipart/form-data belgilaydi
        }
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      return response.json();
    },

    // PATCH FormData bilan
    async patchFormData<T>(endpoint: string, formData: FormData): Promise<T> {
      const response = await makeAuthenticatedRequest(
        `${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}${endpoint}`,
        {
          method: 'PATCH',
          body: formData,
          // Content-Type ni qo'lda o'rnatmaymiz - brauzer o'zi multipart/form-data belgilaydi
        }
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      return response.json();
    },
  }), [makeAuthenticatedRequest]);

  return {
    ...apiClient,
    isLoading: csrfLoading,
  };
}

// Reviews hook
export function useReviews() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}/reviews/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        // Filter only approved and not deleted reviews
        const approvedReviews = (data.results || []).filter(
          (review: any) => review.approved && !review.deleted
        );
        setReviews(approvedReviews);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    // Fetch only once on mount
    fetchReviews();
  }, []); // Empty dependency to prevent infinite loop

  return { reviews, loading, error };
}

// Restaurant Info hook
export function useRestaurantInfo() {
  const [restaurantInfo, setRestaurantInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchRestaurantInfo = async () => {
      try {
        setLoading(true);
        
        // Add cache-busting to always get fresh data
        const timestamp = new Date().getTime();
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}/restaurant-info/?t=${timestamp}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          cache: 'no-cache',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setRestaurantInfo(data || null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchRestaurantInfo();
    
    // No automatic refresh - data will be fetched on component mount only
  }, []); // Empty dependency array to prevent infinite loop

  return { restaurantInfo, loading, error };
}


// Site Settings hook
export function useSiteSettings() {
  const [siteSettings, setSiteSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchSiteSettings = async () => {
      try {
        setLoading(true);
        
        // Add cache-busting to always get fresh data
        const timestamp = new Date().getTime();
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}/site-settings/?t=${timestamp}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          cache: 'no-cache',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setSiteSettings(data || null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchSiteSettings();
    
    // No automatic refresh - data will be fetched on component mount only
  }, []); // Empty dependency array to prevent infinite loop

  return { siteSettings, loading, error };
}

// Categories hook
export function useCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastFetchTime, setLastFetchTime] = useState(0);

  const fetchCategories = useCallback(async (force = false) => {
    // Prevent excessive API calls - only fetch if more than 5 seconds have passed or forced
    const now = Date.now();
    if (!force && now - lastFetchTime < 5000) {
      console.log('useCategories: Skipping fetch - too recent');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      // Get only active categories for frontend display
      // Add cache-busting to always get fresh data
      const timestamp = new Date().getTime();
      const random = Math.random().toString(36).substring(7);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}/categories/?t=${timestamp}&r=${random}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        cache: 'no-cache', // Added this line
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setCategories(data.results || []);
      setLastFetchTime(now);
    } catch (err) {
      console.error('useCategories: Error fetching categories:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [lastFetchTime]);

  useEffect(() => {
    fetchCategories(true); // Force initial fetch
  }, []); // Empty dependency array to prevent infinite loop

  const refetch = useCallback(() => {
    console.log('useCategories: Force refetch called');
    fetchCategories(true); // Force refetch
  }, [fetchCategories]);

  return { categories, loading, error, refetch };
}

// Admin panel uchun alohida hook - barcha kategoriyalarni olish (o'chirilganlar ham)
export function useAdminCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // Admin uchun barcha kategoriyalarni olish (o'chirilganlar ham)
      const timestamp = new Date().getTime();
      const random = Math.random().toString(36).substring(7);
      const random2 = Math.random().toString(36).substring(7);
      const random3 = Math.random().toString(36).substring(7);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}/categories/?show_all=true&t=${timestamp}&r=${random}&r2=${random2}&r3=${random3}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setCategories(data.results || []);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const refetch = useCallback(() => {
    console.log('useAdminCategories: Force refetch called');
    fetchCategories();
  }, [fetchCategories]);

  return { categories, loading, error, refetch };
}

// Menu Items hook
export function useMenuItems() {
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastFetchTime, setLastFetchTime] = useState(0);

  const fetchMenuItems = useCallback(async (force = false) => {
    // Prevent excessive API calls - only fetch if more than 5 seconds have passed or forced
    const now = Date.now();
    if (!force && now - lastFetchTime < 5000) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const apiUrl = 'https://api.tokyokafe.uz/api';
      
      // Add cache-busting to always get fresh data
      const timestamp = new Date().getTime();
      const response = await fetch(`${apiUrl}/menu-items/?show_all=true&t=${timestamp}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        cache: 'no-cache',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      // Handle both paginated (results) and non-paginated (array) responses
      const items = Array.isArray(data) ? data : (data.results || []);
      setMenuItems(items);
      setLastFetchTime(now);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [lastFetchTime]);

  useEffect(() => {
    fetchMenuItems(true); // Force initial fetch
  }, []); // Empty dependency array to prevent infinite loops

  const refetch = useCallback(() => {
    fetchMenuItems(true); // Force refetch
  }, [fetchMenuItems]);

  return { menuItems, loading, error, refetch };
}

// Admin panel uchun alohida hook - barcha menu itemlarni olish (pagination yo'q)
export function useAdminMenuItems() {
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastFetchTime, setLastFetchTime] = useState(0);

  const fetchMenuItems = useCallback(async (force = false) => {
    // Prevent excessive API calls - only fetch if more than 5 seconds have passed or forced
    const now = Date.now();
    if (!force && now - lastFetchTime < 5000) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const apiUrl = 'https://api.tokyokafe.uz/api';
      
      // Add cache-busting and show_all=true to get all items without pagination
      const timestamp = new Date().getTime();
      const random = Math.random().toString(36).substring(7);
      const random2 = Math.random().toString(36).substring(7);
      const random3 = Math.random().toString(36).substring(7);
      const response = await fetch(`${apiUrl}/menu-items/?show_all=true&t=${timestamp}&r=${random}&r2=${random2}&r3=${random3}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        cache: 'no-cache',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      // When show_all=true, response is a direct array, not paginated
      const items = Array.isArray(data) ? data : (data.results || []);
      setMenuItems(items);
      setLastFetchTime(now);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [lastFetchTime]);

  useEffect(() => {
    fetchMenuItems(true); // Force initial fetch
  }, []); // Empty dependency array to prevent infinite loops

  const refetch = useCallback(() => {
    fetchMenuItems(true); // Force refetch
  }, [fetchMenuItems]);

  return { menuItems, loading, error, refetch };
}

// Single Menu Item hook
export function useMenuItem(id: string | number) {
  const { get } = useApiClient();
  const [menuItem, setMenuItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!id) return;
    
    const fetchMenuItem = async () => {
      try {
        setLoading(true);
        const response = await get<any>(`/menu-items/${id}/`);
        setMenuItem(response);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchMenuItem();
  }, [id]); // Only depend on id, not get function

  return { menuItem, loading, error };
}

// Promotions hook
export function usePromotions() {
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastFetchTime, setLastFetchTime] = useState(0);

  const fetchPromotions = useCallback(async (force = false) => {
    // Prevent excessive API calls - only fetch if more than 5 seconds have passed or forced
    const now = Date.now();
    if (!force && now - lastFetchTime < 5000) {
      console.log('usePromotions: Skipping fetch - too recent');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      // Add cache busting to force fresh data
      const timestamp = new Date().getTime();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.tokyokafe.uz/api'}/promotions/?t=${timestamp}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        cache: 'no-cache',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPromotions(data.results || []);
      setLastFetchTime(now);
    } catch (err) {
      console.error('usePromotions: Error fetching promotions:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [lastFetchTime]);

  useEffect(() => {
    fetchPromotions(true); // Force initial fetch
  }, []); // Empty dependency array to prevent infinite loops

  const refetch = useCallback(() => {
    console.log('usePromotions: Force refetch called');
    fetchPromotions(true); // Force refetch
  }, [fetchPromotions]);

  return { promotions, loading, error, refetch };
}

// Hook ishlatish misoli:
/*
function AdminComponent() {
  const api = useApiClient();

  const handleCreateItem = async (itemData: any) => {
    try {
      const newItem = await api.post('/menu-items/', itemData);
    } catch (error) {
      console.error('Error creating item:', error);
    }
  };

  const handleUpdateItem = async (id: number, itemData: any) => {
    try {
      const updatedItem = await api.patch(`/menu-items/${id}/`, itemData);
    } catch (error) {
      console.error('Error updating item:', error);
    }
  };

  const handleDeleteItem = async (id: number) => {
    try {
      await api.delete(`/menu-items/${id}/`);
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  return (
    <div>
      {api.isLoading && <p>Loading...</p>}
      <button onClick={() => handleCreateItem({ name: 'Test Item' })}>
        Create Item
      </button>
    </div>
  );
}
*/