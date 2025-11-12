# Tokyo Kafe - Optimized Django Settings
# ========================================
# Performance va resurs optimization uchun

# Bu faylni settings.py ga qo'shing yoki import qiling:
# from .settings_optimized import *

import os
from pathlib import Path

# Performance Optimizations
# =========================

# Database Connection Pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # yoki postgresql
        'NAME': 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # 10 daqiqa connection pooling
        'OPTIONS': {
            'timeout': 20,  # SQLite timeout
        }
    }
}

# Cache Configuration (Memory Cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tokyo-kafe-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Session Engine (Cache-based for performance)
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Static & Media Files Optimization
# ==================================

# Beget server yo'llari
BASE_DIR = Path(__file__).resolve().parent.parent
BEGET_USER = 'u1234567'  # O'zingiznikini kiriting

STATIC_ROOT = f'/home/{BEGET_USER}/public_html/backend/staticfiles'
STATIC_URL = '/static/'

MEDIA_ROOT = f'/home/{BEGET_USER}/public_html/backend/media'
MEDIA_URL = '/media/'

# Static files finders optimization
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# File Upload Settings (limit katta fayllar uchun)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# REST Framework Optimization
# ============================

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 200,
    
    # Throttling (so'rovlarni cheklash)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonim foydalanuvchilar uchun
        'user': '1000/hour',  # Ro'yxatdan o'tgan foydalanuvchilar
    },
    
    # Cache for browsable API
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 
        'rest_framework.negotiation.DefaultContentNegotiation',
}

# Middleware Optimization
# =======================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Gzip middleware (Nginx qilsa shart emas)
    # 'django.middleware.gzip.GZipMiddleware',
]

# CORS Settings (Frontend uchun)
# ===============================

CORS_ALLOWED_ORIGINS = [
    "https://tokyokafe.uz",
    "https://www.tokyokafe.uz",
    "http://localhost:3000",  # Development
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
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

# CSRF Settings
# =============

CSRF_TRUSTED_ORIGINS = [
    'https://tokyokafe.uz',
    'https://www.tokyokafe.uz',
]

CSRF_COOKIE_SECURE = True  # HTTPS da
CSRF_COOKIE_HTTPONLY = False  # Frontend access uchun
CSRF_COOKIE_SAMESITE = 'Lax'

# Security Settings (Production)
# ==============================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# HTTPS settings (SSL bo'lganda)
SECURE_SSL_REDIRECT = False  # Nginx qiladi
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging (Performance uchun minimal)
# ====================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',  # Faqat WARNING va yuqori
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'/home/{BEGET_USER}/public_html/backend/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'simple',
        },
        'console': {
            'level': 'ERROR',  # Faqat ERROR console ga
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Template Optimization
# =====================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # Template caching (production)
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

# Allowed Hosts
# =============

ALLOWED_HOSTS = [
    'tokyokafe.uz',
    'www.tokyokafe.uz',
    'api.tokyokafe.uz',
    'localhost',
    '127.0.0.1',
]

# Debug (Production da False)
# ============================

DEBUG = False

# Agar resurs muammosi bo'lsa, quyidagilarni qo'shing:
# ======================================================

# Disable admin autodiscover (agar admin ishlatmasangiz)
# ADMIN_ENABLED = False

# Compress images automatically (django-imagekit bilan)
# IMAGEKIT_DEFAULT_CACHEFILE_BACKEND = 'imagekit.cachefiles.backends.Simple'

# Use persistent database connections
# CONN_MAX_AGE = 600

print("✅ Optimized settings yuklandi!")

