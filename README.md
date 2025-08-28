# Docker Development Environment Setup

This Docker setup provides a containerized development environment for the Learning Platform project, designed for the Systems Thinking workshop.

## Architecture

The containerized environment includes:
- **API Container**: Django REST API with Python 3.11.11
- **Database Container**: PostgreSQL 15 

## Prerequisites

1. **Docker & Docker Compose**: Install Docker Desktop or Docker Engine + Docker Compose
2. **GitHub OAuth App**: Create a GitHub OAuth application for authentication
3. **Environment Variables**: Copy and configure the environment template

## Quick Start

### 1. Setup Environment Variables

```bash
# Copy the environment template
cp .env.docker.template .env

# Edit .env with your actual values (especially GitHub OAuth credentials)
```

### 2. Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 3. Access the Application

- **API**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **Database**: localhost:5432 (accessible for external tools)

### 4. Admin Access

Use the credentials from your `.env` file:
- Username: Value of `LEARN_OPS_SUPERUSER_NAME`
- Password: Value of `LEARN_OPS_SUPERUSER_PASSWORD`

## Virtual Environment Workflow

This Docker setup maintains the pipenv virtual environment workflow that students encounter in local development.

### Key Learning Concepts:
1. **Virtual Environment**: All Django commands run through `pipenv`
2. **Service Dependencies**: API depends on database health
3. **Environment Variables**: Configuration through Docker environment

### Essential Commands:

```bash
# Start services
docker-compose up -d

# Access virtual environment (same as local: pipenv shell)
docker-compose exec api pipenv shell

# Run Django commands (same as local: pipenv run python manage.py ...)
docker-compose exec api pipenv run python manage.py migrate
docker-compose exec api pipenv run python manage.py shell
docker-compose exec api pipenv run python manage.py loaddata complete_backup

# View logs
docker-compose logs -f
docker-compose logs -f api

# Stop services
docker-compose down
```

### Daily Development

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f db
```

### Database Operations

```bash
# Run migrations
docker-compose exec api pipenv run python manage.py migrate

# Load fixtures
docker-compose exec api pipenv run python manage.py loaddata complete_backup

# Access database shell
docker-compose exec db psql -U learnopsdev -d learnopsdev

# Access Django shell
docker-compose exec api pipenv run python manage.py shell
```

### Code Changes

The API container uses volume mounts, so code changes are immediately reflected without rebuilding. However, if you modify:

- `Pipfile` or `Pipfile.lock`: Rebuild with `docker-compose up --build api`
- Django settings: Restart with `docker-compose restart api`

## Container Details

### API Container (learn-ops-api)

- **Image**: Custom build from Python 3.11.11
- **Port**: 8000
- **Features**:
  - Hot reload for development
  - Automatic database setup and migrations
  - Pre-loaded fixtures for development data
  - Health checks for service dependencies

### Database Container (learn-ops-db)

- **Image**: PostgreSQL 15
- **Port**: 5432
- **Features**:
  - Persistent data storage
  - Health checks
  - Ready for external connections

### Message Broker Container (learn-ops-message-broker)

- **Image**: Valkey 7.2 (Redis-compatible)
- **Port**: 6379
- **Purpose**: Future microservices communication

## Future Expansion

The docker-compose.yml includes commented placeholders for:

### React Client Container
```yaml
# Uncomment and modify when ready
client:
  build:
    context: ../learn-ops-client
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
```

### Microservice Container
```yaml
# Uncomment and modify when ready
microservice:
  build:
    context: ../learn-ops-microservice
    dockerfile: Dockerfile
  ports:
    - "8001:8001"
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database health
   docker-compose ps
   docker-compose logs db
   ```

2. **Port Conflicts**
   ```bash
   # Check if ports are in use
   lsof -i :8000
   lsof -i :5432
   lsof -i :6379
   ```

3. **Permission Issues**
   ```bash
   # Fix entrypoint permissions
   chmod +x entrypoint.sh
   ```

### Useful Commands

```bash
# Clean restart
docker-compose down -v
docker-compose up --build

# Access container shell with activated virtual environment
docker-compose exec api pipenv shell

# Run Django commands within virtual environment
docker-compose exec api pipenv run python manage.py shell
docker-compose exec api pipenv run python manage.py dbshell
docker-compose exec api pipenv run python manage.py collectstatic

# Access container bash (without virtual environment activated)
docker-compose exec api bash

# View container resource usage
docker stats
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `LEARN_OPS_CLIENT_ID` | GitHub OAuth Client ID | Required |
| `LEARN_OPS_SECRET_KEY` | GitHub OAuth Secret | Required |
| `LEARN_OPS_DJANGO_SECRET_KEY` | Django Secret Key | Required |
| `LEARN_OPS_DB` | Database Name | learnopsdev |
| `LEARN_OPS_USER` | Database User | learnopsdev |
| `LEARN_OPS_PASSWORD` | Database Password | password |
| `LEARN_OPS_SUPERUSER_NAME` | Admin Username | admin |
| `LEARN_OPS_SUPERUSER_PASSWORD` | Admin Password | admin123 |

## Security Notes

- This setup is designed for **LOCAL DEVELOPMENT ONLY**
- Never use these configurations in production
- Database credentials are simple for development convenience
- GitHub OAuth should use localhost callbacks only