"""
Gunicorn configuration for production deployment
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
# For Render.com free tier, use fewer workers to avoid resource issues
workers = int(os.getenv('WEB_CONCURRENCY', min(4, multiprocessing.cpu_count() * 2 + 1)))
worker_class = 'sync'
worker_connections = 1000
timeout = 120  # Increased timeout for email sending operations (2 minutes)
keepalive = 5
graceful_timeout = 30  # Time to wait for workers to finish before killing them

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'ereceipt-backend'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

