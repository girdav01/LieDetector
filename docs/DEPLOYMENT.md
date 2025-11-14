# SocialGuard Deployment Guide

## Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- Redis server (optional but recommended)
- Docker (optional, for containerized deployment)

## Development Deployment

### 1. Backend API

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (optional)
redis-server

# Run the API
python main.py

# API available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Frontend available at: http://localhost:3000
```

### 3. Chrome Extension

1. Open Chrome browser
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked"
5. Select the `extension` directory
6. Extension is now active

## Production Deployment

### Docker Deployment

#### Backend + Redis

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  api:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    restart: unless-stopped

volumes:
  redis-data:
```

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy:

```bash
docker-compose up -d
```

### Kubernetes Deployment

#### Backend Deployment

`k8s/backend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: socialguard-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: socialguard-api
  template:
    metadata:
      labels:
        app: socialguard-api
    spec:
      containers:
      - name: api
        image: socialguard/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: "redis-service"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: socialguard-api-service
spec:
  selector:
    app: socialguard-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### Redis Deployment

`k8s/redis-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - protocol: TCP
    port: 6379
    targetPort: 6379
```

Deploy to Kubernetes:

```bash
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
```

### Nginx Reverse Proxy

`nginx.conf`:

```nginx
upstream socialguard_api {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.socialguard.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.socialguard.example.com;

    ssl_certificate /etc/ssl/certs/socialguard.crt;
    ssl_certificate_key /etc/ssl/private/socialguard.key;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://socialguard_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Environment Configuration

### Backend Environment Variables

Create `.env` file:

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_password
REDIS_DB=0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Security
SECRET_KEY=your_secret_key_here
API_KEY_REQUIRED=true

# CORS
CORS_ORIGINS=["https://app.socialguard.example.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/socialguard/api.log

# ML Models
MODEL_PATH=/app/models
MODEL_UPDATE_INTERVAL=86400  # 24 hours
```

Load environment variables in `main.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
```

## SSL/TLS Configuration

### Generate Self-Signed Certificate (Development)

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem \
  -keyout key.pem \
  -days 365 \
  -subj "/CN=localhost"
```

### Let's Encrypt (Production)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.socialguard.example.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring & Logging

### Prometheus Metrics

Add to `backend/main.py`:

```python
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

# Instrument app
Instrumentator().instrument(app).expose(app)

# Custom metrics
trust_score_requests = Counter('trust_score_requests_total', 'Total trust score requests')
trust_score_duration = Histogram('trust_score_duration_seconds', 'Trust score calculation duration')
```

Access metrics at `http://localhost:8000/metrics`

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler(
    'socialguard.log',
    maxBytes=10000000,  # 10MB
    backupCount=5
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

handler.setFormatter(formatter)
logger = logging.getLogger('socialguard')
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### ELK Stack Integration

```yaml
# docker-compose.elk.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
```

## Performance Optimization

### Redis Optimization

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save ""  # Disable RDB snapshots for pure cache
appendonly yes
appendfsync everysec
```

### API Optimization

```python
# Enable response caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Cache responses
from fastapi_cache.decorator import cache

@app.get("/trust_score/{event_id}")
@cache(expire=3600)
async def get_trust_score(event_id: str):
    ...
```

### Database Connection Pooling

```python
from redis import ConnectionPool

pool = ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50,
    decode_responses=True
)

r = redis.Redis(connection_pool=pool)
```

## Chrome Extension Distribution

### Package Extension

```bash
cd extension
zip -r socialguard-extension.zip * -x "*.git*" "node_modules/*"
```

### Chrome Web Store Deployment

1. Create developer account at [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/developer/dashboard)
2. Pay one-time $5 registration fee
3. Upload `socialguard-extension.zip`
4. Fill in store listing details
5. Submit for review

### Enterprise Deployment

For internal deployment:

1. Host CRX file on internal server
2. Configure Chrome policy:

```json
{
  "ExtensionInstallForcelist": [
    "extensionid;https://internal-server.com/socialguard.crx"
  ]
}
```

## Health Checks

### API Health Endpoint

```python
@app.get("/health")
async def health_check():
    # Check Redis connection
    try:
        r.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"

    return {
        "status": "healthy",
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Backup & Recovery

### Redis Backup

```bash
# Enable AOF persistence
redis-cli CONFIG SET appendonly yes

# Manual backup
redis-cli BGSAVE

# Automated backups
0 2 * * * redis-cli BGSAVE && cp /var/lib/redis/dump.rdb /backup/
```

### Database Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=/backup/socialguard
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Redis
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Compress
gzip $BACKUP_DIR/redis_$DATE.rdb

# Keep last 7 days
find $BACKUP_DIR -name "redis_*.rdb.gz" -mtime +7 -delete
```

## Troubleshooting

### Common Issues

1. **Redis connection failed**
   ```bash
   # Check Redis status
   redis-cli ping

   # Check connection
   telnet localhost 6379
   ```

2. **High API latency**
   ```bash
   # Check Redis latency
   redis-cli --latency

   # Monitor slow queries
   redis-cli SLOWLOG GET 10
   ```

3. **Extension not detecting threats**
   - Check browser console for errors
   - Verify content script is injected
   - Test API endpoint connectivity

### Logs Location

- API logs: `/var/log/socialguard/api.log`
- Redis logs: `/var/log/redis/redis.log`
- Nginx logs: `/var/log/nginx/access.log`
- Extension logs: Chrome DevTools Console

## Security Checklist

- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable API authentication
- [ ] Rotate secrets regularly
- [ ] Set up security monitoring
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Implement backup strategy
- [ ] Set up intrusion detection

## Support

For deployment issues:
- Check logs first
- Review health check endpoints
- Verify network connectivity
- Consult documentation
- Open GitHub issue if needed
