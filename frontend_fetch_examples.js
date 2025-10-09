// Tokyo Kafe - Frontend Fetch Examples (Vercel)
// ==============================================
// Vercel'dagi Next.js dan Beget backend ga fetch qilish

// ==========================================
// 1. Environment Variables (.env.local)
// ==========================================

// .env.local faylida (Vercel Environment Variables ga ham qo'shing):
// NEXT_PUBLIC_API_URL=https://tokyokafe.uz

// ==========================================
// 2. API Client Setup
// ==========================================

// lib/api.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://tokyokafe.uz'

// CSRF token olish
function getCookie(name) {
  if (typeof document === 'undefined') return null
  
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

// CSRF token olish (backenddan)
export async function getCSRFToken() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/csrf/`, {
      method: 'GET',
      credentials: 'include', // MUHIM: Cookie yuborish uchun
    })
    
    if (response.ok) {
      const data = await response.json()
      return data.csrfToken || getCookie('csrftoken')
    }
  } catch (error) {
    console.error('CSRF token error:', error)
  }
  return getCookie('csrftoken')
}

// ==========================================
// 3. GET Request (Menu)
// ==========================================

export async function fetchMenu() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/menu/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // MUHIM: Session uchun
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Menu fetch error:', error)
    throw error
  }
}

// ==========================================
// 4. POST Request (Cart ga qo'shish)
// ==========================================

export async function addToCart(itemId, quantity = 1) {
  const csrfToken = await getCSRFToken()
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/cart/add/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken, // CSRF token
      },
      credentials: 'include', // MUHIM: Cookie va session uchun
      body: JSON.stringify({
        item_id: itemId,
        quantity: quantity,
      }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to add to cart')
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Add to cart error:', error)
    throw error
  }
}

// ==========================================
// 5. React Component Misol
// ==========================================

// components/Menu.jsx
import { useState, useEffect } from 'react'
import { fetchMenu, addToCart } from '@/lib/api'

export default function Menu() {
  const [menu, setMenu] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Menu yuklash
  useEffect(() => {
    loadMenu()
  }, []) // [] dependency - faqat birinchi render da
  
  async function loadMenu() {
    try {
      setLoading(true)
      const data = await fetchMenu()
      setMenu(data)
      setError(null)
    } catch (err) {
      setError(err.message)
      console.error('Load menu error:', err)
    } finally {
      setLoading(false)
    }
  }
  
  // Cart ga qo'shish
  async function handleAddToCart(itemId) {
    try {
      const result = await addToCart(itemId, 1)
      alert('Mahsulot savatga qo\'shildi!')
      console.log('Cart:', result)
    } catch (err) {
      alert('Xatolik: ' + err.message)
    }
  }
  
  if (loading) return <div>Yuklanmoqda...</div>
  if (error) return <div>Xatolik: {error}</div>
  
  return (
    <div>
      <h1>Menu</h1>
      <div className="grid grid-cols-3 gap-4">
        {menu.map((item) => (
          <div key={item.id} className="border p-4 rounded">
            <h3>{item.name}</h3>
            <p>{item.price} so'm</p>
            <button 
              onClick={() => handleAddToCart(item.id)}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              Savatga qo'shish
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

// ==========================================
// 6. SWR bilan (fetch loop ni oldini olish)
// ==========================================

// npm install swr

import useSWR from 'swr'

const fetcher = (url) => 
  fetch(url, { credentials: 'include' }).then((r) => r.json())

export function MenuWithSWR() {
  const { data, error, isLoading } = useSWR(
    `${API_BASE_URL}/api/menu/`,
    fetcher,
    {
      revalidateOnFocus: false,      // Tab switch da fetch qilmaslik
      revalidateOnReconnect: false,  // Reconnect da fetch qilmaslik
      refreshInterval: 0,            // Auto refresh yo'q
    }
  )
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return (
    <div>
      {data?.map((item) => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  )
}

// ==========================================
// 7. React Query bilan
// ==========================================

// npm install @tanstack/react-query

import { useQuery, useMutation } from '@tanstack/react-query'

export function MenuWithReactQuery() {
  // Menu query
  const { data, isLoading, error } = useQuery({
    queryKey: ['menu'],
    queryFn: fetchMenu,
    staleTime: 5 * 60 * 1000, // 5 daqiqa fresh
    refetchOnWindowFocus: false,
  })
  
  // Add to cart mutation
  const addToCartMutation = useMutation({
    mutationFn: ({ itemId, quantity }) => addToCart(itemId, quantity),
    onSuccess: () => {
      alert('Savatga qo\'shildi!')
    },
    onError: (error) => {
      alert('Xatolik: ' + error.message)
    },
  })
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error</div>
  
  return (
    <div>
      {data?.map((item) => (
        <div key={item.id}>
          <h3>{item.name}</h3>
          <button 
            onClick={() => addToCartMutation.mutate({ itemId: item.id, quantity: 1 })}
            disabled={addToCartMutation.isPending}
          >
            {addToCartMutation.isPending ? 'Qo\'shilmoqda...' : 'Savatga qo\'shish'}
          </button>
        </div>
      ))}
    </div>
  )
}

// ==========================================
// 8. Axios bilan (opsional)
// ==========================================

// npm install axios

import axios from 'axios'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Cookie va session uchun
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor (CSRF token qo'shish)
api.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrftoken')
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
})

// Response interceptor (error handling)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403) {
      console.error('CSRF error - token invalid')
    }
    return Promise.reject(error)
  }
)

// Usage
export async function fetchMenuAxios() {
  const response = await api.get('/api/menu/')
  return response.data
}

export async function addToCartAxios(itemId, quantity) {
  const response = await api.post('/api/cart/add/', {
    item_id: itemId,
    quantity: quantity,
  })
  return response.data
}

// ==========================================
// 9. CSRF Endpoint (Backend - Django)
// ==========================================

// Backend'da CSRF token berish uchun endpoint yarating:

/*
# views.py
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})

# urls.py
urlpatterns = [
    path('api/csrf/', get_csrf_token, name='csrf'),
]
*/

// ==========================================
// 10. Common Errors va Yechimlar
// ==========================================

/*
ERROR: "Origin does not match any trusted origins"
FIX: settings.py da CSRF_TRUSTED_ORIGINS ga Vercel URL qo'shing

ERROR: "CSRF token missing or incorrect"
FIX: 
  - credentials: 'include' qo'shing
  - X-CSRFToken header qo'shing
  - CSRF_COOKIE_HTTPONLY = False

ERROR: "Too many requests"
FIX:
  - useEffect dependency [] qo'ying
  - SWR yoki React Query ishlatib caching qiling

ERROR: "No 'Access-Control-Allow-Origin' header"
FIX:
  - CORS_ALLOW_CREDENTIALS = True
  - CORS_ALLOWED_ORIGINS ga Vercel URL qo'shing
*/

console.log('✅ Frontend fetch examples yuklandi!')

