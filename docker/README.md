# Docker Configuration

This directory contains all Docker-related configurations for the Learning Platform API, organized for clarity and maintainability.

## Directory Structure

```
docker/
├── dev/                           # Development environment
│   ├── docker-compose.dev.yml     # Development services
│   └── Dockerfile.dev             # Development container
├── prod/                          # Production environment  
│   ├── docker-compose.prod.yml    # Production services
│   ├── Dockerfile.prod            # Production container
│   ├── entrypoint.prod.sh         # Production startup script
│   └── .env.template.prod         # Production environment template
├── config/                        # Configuration files
│   ├── nginx/                     # Nginx reverse proxy config
│   └── supervisor/                # Process management config
└── scripts/                       # Utility scripts
    └── backup.sh                  # Database backup script
```

## Quick Commands

### Development
```bash
# From project root
docker-compose -f docker/dev/docker-compose.dev.yml up -d
docker-compose -f docker/dev/docker-compose.dev.yml logs -f api
docker-compose -f docker/dev/docker-compose.dev.yml exec api python manage.py migrate
```

### Production  
```bash
# From project root
docker-compose -f docker/prod/docker-compose.prod.yml up -d
docker-compose -f docker/prod/docker-compose.prod.yml logs api
docker-compose -f docker/prod/docker-compose.prod.yml ps
```

## Environment Files

- **Development**: Uses root `.env` file
- **Production**: Uses `docker/prod/.env.prod` file (create from template)

## Important Notes

- All paths in Docker Compose files are relative to the project root
- Configuration files are organized by service type
- Production images use multi-stage builds for security and size optimization
- Both environments include health checks and proper logging

For detailed setup instructions, see the main `DOCKER_SETUP.md` file in the project root.