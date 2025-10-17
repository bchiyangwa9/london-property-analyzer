# 🚀 Deployment Guide

Complete guide for deploying the London Property Search Analyzer to production environments.

## 🌐 Deployment Options

### 1. Streamlit Cloud (Recommended)

**Best for**: Quick deployment, free hosting, GitHub integration

#### Prerequisites
- GitHub account
- Public GitHub repository with your code

#### Steps
1. **Prepare Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/london-property-analyzer.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "Deploy an app"
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configuration**
   - App will auto-deploy from GitHub
   - Updates push automatically
   - Custom domain available (paid plans)

#### Pros & Cons
✅ **Pros**: Free, easy, automatic updates, built-in SSL
❌ **Cons**: Limited resources, public repos only (free tier)

### 2. Heroku Deployment

**Best for**: Scalable deployment, custom domains, advanced features

#### Prerequisites
- Heroku account
- Heroku CLI installed
- Git repository

#### Steps
1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku

   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli

   # Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Configure Buildpacks**
   ```bash
   heroku buildpacks:set heroku/python
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

5. **Open Application**
   ```bash
   heroku open
   ```

#### Environment Variables
Set configuration through Heroku dashboard or CLI:
```bash
heroku config:set ENVIRONMENT=production
heroku config:set DEBUG=false
```

#### Pros & Cons
✅ **Pros**: Scalable, custom domains, database add-ons
❌ **Cons**: Costs money, more complex setup

### 3. Docker Deployment

**Best for**: Consistent environments, containerized deployment

#### Dockerfile
Create `Dockerfile` in project root:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Docker Compose (Optional)
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
```

#### Build and Run
```bash
# Build image
docker build -t london-property-analyzer .

# Run container
docker run -p 8501:8501 london-property-analyzer

# Or with docker-compose
docker-compose up -d
```

### 4. AWS EC2 Deployment

**Best for**: Full control, enterprise deployment

#### Steps
1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - Select appropriate instance size (t3.medium recommended)
   - Configure security groups (port 8501, 22, 80, 443)

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip

   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python and pip
   sudo apt install python3.11 python3.11-pip git -y

   # Clone repository
   git clone https://github.com/yourusername/london-property-analyzer.git
   cd london-property-analyzer

   # Install dependencies
   pip3 install -r requirements.txt
   ```

3. **Run with Screen/Tmux**
   ```bash
   # Install screen
   sudo apt install screen -y

   # Start screen session
   screen -S property-analyzer

   # Run application
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0

   # Detach with Ctrl+A, then D
   ```

4. **Setup Nginx (Optional)**
   ```bash
   sudo apt install nginx -y

   # Create nginx config
   sudo nano /etc/nginx/sites-available/property-analyzer
   ```

   Nginx configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### 5. Google Cloud Platform (GCP)

**Best for**: Google ecosystem integration, cloud-native features

#### Cloud Run Deployment
1. **Enable APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

2. **Build and Deploy**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/london-property-analyzer
   gcloud run deploy --image gcr.io/PROJECT_ID/london-property-analyzer --platform managed
   ```

#### App Engine Deployment
Create `app.yaml`:
```yaml
runtime: python311

env_variables:
  ENVIRONMENT: production

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

Deploy:
```bash
gcloud app deploy
```

## ⚙️ Configuration for Production

### Environment Variables
Set these in your production environment:

```bash
# Application settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security (if using real APIs)
API_KEY=your-api-key
SECRET_KEY=your-secret-key

# Database (if added)
DATABASE_URL=postgresql://user:pass@host:5432/db

# Email (if using real email service)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

### Security Considerations

#### SSL/HTTPS Setup
For production deployments:
1. **Use SSL certificates** (Let's Encrypt for free SSL)
2. **Force HTTPS** redirects
3. **Secure headers** in web server configuration

#### API Security
If connecting to real APIs:
```python
import os
from urllib.parse import urlparse

# Validate API endpoints
def validate_api_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ['https'] and parsed.netloc

# Use environment variables
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
```

#### Rate Limiting
Implement rate limiting for production:
```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window=3600):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    def is_allowed(self, client_ip):
        now = time.time()
        client_requests = self.requests[client_ip]

        # Remove old requests
        client_requests[:] = [req_time for req_time in client_requests 
                             if now - req_time < self.window]

        if len(client_requests) >= self.max_requests:
            return False

        client_requests.append(now)
        return True
```

### Performance Optimization

#### Caching Strategy
```python
import streamlit as st
from functools import lru_cache

# Cache expensive operations
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_market_data():
    # Expensive data loading operation
    return data

@lru_cache(maxsize=128)
def calculate_statistics(data_hash):
    # Expensive calculations
    return stats
```

#### Database Configuration
For production with real database:
```python
import os
import sqlalchemy as sa
from sqlalchemy.pool import QueuePool

# Production database connection
DATABASE_URL = os.getenv('DATABASE_URL')
engine = sa.create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Monitoring and Logging

#### Application Logging
```python
import logging
import os

# Configure logging for production
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use throughout application
logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

#### Health Checks
Add health check endpoint:
```python
import streamlit as st
from datetime import datetime

def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }
```

#### Error Tracking
For production error monitoring:
```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Configure Sentry (optional)
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[LoggingIntegration(level=logging.INFO)]
    )
```

## 📊 Scaling Considerations

### Horizontal Scaling
For high-traffic deployments:

1. **Load Balancer**: Distribute traffic across multiple instances
2. **Containerization**: Use Docker for consistent deployments
3. **Database**: Separate database server for data persistence
4. **Caching**: Redis/Memcached for session and data caching

### Performance Monitoring
Set up monitoring for:
- **Response times**: Track API and page load times
- **Memory usage**: Monitor for memory leaks
- **CPU utilization**: Ensure adequate resources
- **Error rates**: Track application errors

### Backup Strategy
Implement regular backups:
- **Database backups**: Automated daily/weekly backups
- **Application code**: Git repository as source of truth
- **User data**: Regular export of user-generated content
- **Configuration**: Version-controlled configuration files

## 🔧 Troubleshooting Deployment

### Common Issues

#### Port Binding Errors
```bash
# Error: Port already in use
# Solution: Use environment variable for port
PORT = int(os.getenv('PORT', 8501))
```

#### Memory Issues
```bash
# Error: Out of memory
# Solutions:
# 1. Increase instance size
# 2. Optimize data loading
# 3. Implement pagination
# 4. Use data streaming
```

#### SSL Certificate Issues
```bash
# Error: SSL certificate verification failed
# Solutions:
# 1. Update certificates
# 2. Check certificate chain
# 3. Verify domain configuration
```

### Deployment Checklist

#### Pre-deployment
- [ ] All tests pass
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Backup strategy in place
- [ ] Monitoring configured

#### Post-deployment
- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] Performance metrics normal
- [ ] Error tracking active
- [ ] Backup verification

## 📞 Support and Maintenance

### Regular Maintenance
- **Security updates**: Monthly security patches
- **Dependency updates**: Quarterly dependency reviews
- **Performance reviews**: Monthly performance analysis
- **Backup testing**: Quarterly backup restoration tests

### Support Channels
- **Technical Issues**: GitHub Issues
- **Security Concerns**: Direct email contact
- **Feature Requests**: GitHub Discussions
- **Documentation**: Wiki and guides

---

**🚀 This guide covers comprehensive deployment strategies for the London Property Search Analyzer. Choose the deployment method that best fits your requirements and technical expertise.**
