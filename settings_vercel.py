# Tokyo Kafe - Django Settings for Vercel Frontend + Beget Backend
# ==================================================================
# Beget serverda Django backend uchun to'liq sozlamalar

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# CORS & CSRF Settings (Vercel uchun)
# ==========================================

# CSRF Trusted Origins - Vercel frontend qo'shilgan
CSRF_TRUSTED_ORIGINS = [
    "https://tokyokafe.uz",
    "https://www.tokyokafe.uz",
    "https://tokyokafe.vercel.app",        # Vercel frontend
    "https://tokyo-kafe.vercel.app",       # Agar boshqa nom bo'lsa
    "https://*.vercel.app",                 # Barcha Vercel preview deployments
]

# CORS Allowed Origins
CORS_ALLOWED_ORIGINS = [
    "https://tokyokafe.uz",
    "https://www.tokyokafe.uz",
    "https://tokyokafe.vercel.app",
    "https://tokyo-kafe.vercel.app",
    "http://localhost:3000",                # Local development
    "http://localhost:3001",
]

# CORS Settings
CORS_ALLOW_CREDENTIALS = True  # Cookie va session uchun MUHIM!
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF Cookie Settings
CSRF_COOKIE_SECURE = True           # HTTPS uchun
CSRF_COOKIE_HTTPONLY = False        # Frontend access uchun FALSE
CSRF_COOKIE_SAMESITE = 'None'       # Cross-site uchun 'None'
CSRF_USE_SESSIONS = False           # Cookie-based CSRF

# Session Cookie Settings
SESSION_COOKIE_SECURE = True        # HTTPS uchun
SESSION_COOKIE_HTTPONLY = True      # XSS himoya
SESSION_COOKIE_SAMESITE = 'None'    # Cross-site uchun 'None'
SESSION_COOKIE_AGE = 1209600        # 2 hafta

# ==========================================
# Installed Apps
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',              # CORS uchun
    'django_filters',
    
    # Your apps
    'menu',
]

# ==========================================
# Middleware (CORS yuqorida bo'lishi kerak!)
# ==========================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',        # ENG YUQORIDA!
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==========================================
# Database (Beget)
# ==========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# ==========================================
# Static & Media Files
# ==========================================

BEGET_USER = 'u1234567'  # O'ZGARTIRING!

STATIC_URL = '/static/'
STATIC_ROOT = f'/home/{BEGET_USER}/public_html/backend/staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = f'/home/{BEGET_USER}/public_html/backend/media'

# ==========================================
# REST Framework Settings
# ==========================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 200,
    
    # Throttling - "Too many requests" ni oldini olish
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Anonim: 100 so'rov/soat
        'user': '1000/hour',     # User: 1000 so'rov/soat
    },
}

# ==========================================
# Cache Configuration
# ==========================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tokyo-kafe-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# ==========================================
# Security Settings
# ==========================================

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

ALLOWED_HOSTS = [
    'tokyokafe.uz',
    'www.tokyokafe.uz',
    'api.tokyokafe.uz',
    'localhost',
    '127.0.0.1',
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# HTTPS settings
SECURE_SSL_REDIRECT = False  # Nginx qiladi
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==========================================
# Logging
# ==========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'/home/{BEGET_USER}/public_html/backend/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'WARNING',
    },
}

# ==========================================
# Internationalization
# ==========================================

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# ==========================================
# Default primary key field type
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# IMPORTANT NOTES
# ==========================================

"""
1. CSRF_COOKIE_SAMESITE = 'None' va SESSION_COOKIE_SAMESITE = 'None'
   Bu Vercel + Beget cross-domain uchun MUHIM!

2. CSRF_COOKIE_HTTPONLY = False
   Frontend JavaScript CSRF token o'qiy olishi uchun

3. CORS_ALLOW_CREDENTIALS = True
   Cookie va session yuborish uchun

4. corsheaders.middleware.CorsMiddleware
   Eng yuqori middleware bo'lishi kerak!

5. Vercel preview URLs uchun:
   CSRF_TRUSTED_ORIGINS ga "https://*.vercel.app" qo'shing
"""

print("✅ Vercel + Beget settings yuklandi!")

