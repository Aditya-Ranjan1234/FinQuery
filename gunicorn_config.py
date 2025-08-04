# Gunicorn configuration
import multiprocessing

# Server socket
import os
port = int(os.environ.get('PORT', 10000))
bind = f'0.0.0.0:{port}'

# Worker processes
workers = 2  # Adjust based on your Render instance's CPU
worker_class = 'gthread'
threads = 4  # Adjust based on your application's I/O
worker_connections = 1000

# Timeouts
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Server mechanics
chdir = '/opt/render/project/src'
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
