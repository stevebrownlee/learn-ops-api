# Docker Setup Guide for Learning Platform API

This guide explains how to use the new Docker configurations for local development and production deployment.

## Local Development Setup

### Prerequisites
- Docker and Docker Compose installed
- `.env` file configured (copy from `.env.template`)

### Quick Start
```bash
# Start development environment
docker-compose -f docker/dev/docker-compose.dev.yml up -d

# View logs
docker-compose -f docker/dev/docker-compose.dev.yml logs -f api

# Stop environment
docker-compose -f docker/dev/docker-compose.dev.yml down
```

### What You Get
- **Django API**: http://localhost:8000 (with hot reloading)
- **PostgreSQL**: localhost:5432
- **Valkey/Redis**: localhost:6379  
- **Mailhog**: http://localhost:8025 (email testing)

### Development Commands
```bash
# Run migrations
docker-compose -f docker/dev/docker-compose.dev.yml exec api python manage.py migrate

# Create superuser
docker-compose -f docker/dev/docker-compose.dev.yml exec api python manage.py createsuperuser

# Run tests
docker-compose -f docker/dev/docker-compose.dev.yml exec api python manage.py test

# Access Django shell
docker-compose -f docker/dev/docker-compose.dev.yml exec api python manage.py shell

# Load fixtures
docker-compose -f docker/dev/docker-compose.dev.yml exec api python manage.py loaddata fixtures/complete_backup.json
```

## Production Deployment

### GitHub Actions Workflow

The new workflow (`docker-build-deploy.yml`) handles:

1. **Build**: Creates production Docker image
2. **Security Scan**: Runs Trivy vulnerability scanning
3. **Deploy**: Deploys to your DigitalOcean droplet
4. **Cleanup**: Removes old images and containers

### Required GitHub Secrets

Set these in your repository Settings → Secrets and variables → Actions:

```bash
# Django Configuration
DJANGO_SECRET_KEY=your_django_secret_key
ALLOWED_HOSTS=learning.nss.team,api.learning.nss.team

# Database Configuration  
DB_NAME=learning_platform_prod
DB_USER=learning_user
DB_PASSWORD=secure_database_password
DB_HOST=postgres
DB_PORT=5432

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_SECRET_KEY=your_github_oauth_secret
GITHUB_CALLBACK_URL=https://learning.nss.team/auth/github

# Admin User
SUPERUSER_NAME=admin
SUPERUSER_PASSWORD=secure_admin_password

# Optional
SLACK_TOKEN=your_slack_token
```

### Self-Hosted Runner Setup

On your DigitalOcean droplet:

1. **Install Docker** (if not already installed):
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Install GitHub Actions Runner**:
   - Go to your repository Settings → Actions → Runners
   - Click "New self-hosted runner"
   - Follow the installation instructions for Linux

3. **Start the runner service**:
   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

### Manual Production Deployment

If you prefer manual deployment:

```bash
# On your DigitalOcean droplet
git clone https://github.com/your-username/learning-platform-api.git
cd learning-platform-api

# Create production environment file
cp docker/prod/.env.template.prod docker/prod/.env.prod
# Edit docker/prod/.env.prod with your actual values

# Set environment variables for image
export DOCKER_REGISTRY=ghcr.io
export GITHUB_REPOSITORY=your-username/learning-platform-api
export IMAGE_TAG=latest

# Deploy
docker-compose -f docker/prod/docker-compose.prod.yml up -d

# Check status
docker-compose -f docker/prod/docker-compose.prod.yml ps
```

## Production Features

### Security
- Multi-stage Docker build (smaller image size)
- Non-root user execution
- Nginx reverse proxy with rate limiting
- Security headers configured
- Automated vulnerability scanning

### Monitoring
- Health checks for all services
- Structured logging to files
- Log rotation configured
- Container restart policies

### Backups
- Automated daily PostgreSQL backups
- 7-day retention policy
- Backups stored in `./backups` directory

### Performance
- Gunicorn with gevent workers
- Nginx caching for static files
- Database connection pooling
- Redis/Valkey caching

## Troubleshooting

### Development Issues

**Port conflicts:**
```bash
# Change ports in docker/dev/docker-compose.dev.yml if needed
docker-compose -f docker/dev/docker-compose.dev.yml down
docker-compose -f docker/dev/docker-compose.dev.yml up -d
```

**Database connection issues:**
```bash
# Reset database
docker-compose -f docker/dev/docker-compose.dev.yml down -v
docker-compose -f docker/dev/docker-compose.dev.yml up -d
```

### Production Issues

**Check application logs:**
```bash
docker-compose -f docker/prod/docker-compose.prod.yml logs api
```

**Check database connection:**
```bash
docker-compose -f docker/prod/docker-compose.prod.yml exec postgres pg_isready
```

**Restart services:**
```bash
docker-compose -f docker/prod/docker-compose.prod.yml restart api
```

**Health check:**
```bash
curl http://localhost:8000/health/
```

## Migration from Current Setup

1. **Backup your current database**
2. **Update GitHub secrets** as listed above
3. **Push to main branch** - the workflow will automatically build and deploy
4. **Monitor deployment** in GitHub Actions tab
5. **Test the deployed application**

## File Structure

```
├── docker/
│   ├── dev/
│   │   ├── docker-compose.dev.yml  # Local development
│   │   └── Dockerfile.dev          # Development image
│   ├── prod/
│   │   ├── docker-compose.prod.yml # Production deployment
│   │   ├── Dockerfile.prod         # Production image
│   │   ├── entrypoint.prod.sh      # Production startup script
│   │   └── .env.template.prod      # Production environment template
│   ├── config/
│   │   ├── nginx/nginx.prod.conf   # Nginx configuration
│   │   └── supervisor/supervisord.conf # Process management
│   └── scripts/
│       └── backup.sh               # Database backup script
├── docker-compose.observability.yml # Monitoring stack
└── .github/workflows/
    └── docker-build-deploy.yml     # CI/CD pipeline
```

The new setup provides better security, monitoring, and maintainability compared to the current manual deployment process.