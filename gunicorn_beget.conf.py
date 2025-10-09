# Gunicorn configuration for Beget hosting
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes (Beget uchun kam)
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/home/u1234567/public_html/backend/logs/gunicorn_access.log"
errorlog = "/home/u1234567/public_html/backend/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "tokyo_restaurant"

# Server mechanics
daemon = True
pidfile = "/home/u1234567/public_html/backend/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (Beget avtomatik SSL beradi)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    'DJANGO_SETTINGS_MODULE=restaurant_api.settings_beget',
]

# Preload app for better performance
preload_app = True

# Worker timeout
graceful_timeout = 30

# Max worker memory (Beget uchun)
worker_memory_limit = 512  # MB
