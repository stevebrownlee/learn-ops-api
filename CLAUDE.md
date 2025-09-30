# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django REST Framework API for the Learning Platform - an educational management system for Nashville Software School. The API manages cohorts, students, coursework, assessments, and learning records, integrating with GitHub OAuth for authentication.

## Development Setup Commands

**Environment Setup:**
```bash
# Start virtual environment (Python 3.11.11 required)
pipenv --python 3.11.11 shell

# Install dependencies
pipenv install

# Run database migrations
pipenv run migrate
# OR
python manage.py migrate

# Start development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser
```

**Database Operations:**
```bash
# Create new migration after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load fixture data
python manage.py loaddata fixtures/[fixture_name].json
```

**Code Quality:**
```bash
# Run linting
pylint LearningAPI/
```

## Architecture & Code Organization

**Models Structure:**
- `models/people/`: User accounts, cohorts, teams, assessments, student records
- `models/coursework/`: Books, projects, capstones, courses, learning objectives
- `models/skill/`: Core skills tracking, learning records, assessment weights
- `models/tag.py`: Shared tagging system

**Views Structure:**
- `views/`: Main API endpoints organized by feature
- `views/ai/`: AI-related endpoints
- `views/github/`: GitHub integration endpoints
- `views/oauth2/`: OAuth authentication handling

**Key Components:**
- Uses Django REST Framework with token authentication
- PostgreSQL database with extensive migrations history
- GitHub OAuth integration for user authentication
- Structured logging with JSON output
- CORS configured for React client integration

**Database Configuration:**
- Uses environment variables from `.env` file (template: `.env.template`)
- PostgreSQL backend with connection pooling
- Valkey (Redis) for caching

**Authentication:**
- GitHub OAuth via django-allauth
- Token-based API authentication
- Instructor/Student role separation via Django groups

## Environment Variables

Required variables (see `.env.template`):
- `LEARN_OPS_CLIENT_ID`: GitHub OAuth client ID  
- `LEARN_OPS_SECRET_KEY`: GitHub OAuth secret
- `LEARN_OPS_DJANGO_SECRET_KEY`: Django secret key
- `LEARN_OPS_PASSWORD`: Database password
- Database connection vars: `LEARN_OPS_DB`, `LEARN_OPS_USER`, `LEARN_OPS_HOST`, `LEARN_OPS_PORT`
- `LEARN_OPS_SUPERUSER_NAME` & `LEARN_OPS_SUPERUSER_PASSWORD`: Admin credentials

## Key Development Notes

- **Testing**: Basic test structure exists in `LearningAPI/tests.py` but needs expansion
- **Migrations**: Extensive migration history (75+ migrations) - always create migrations for model changes
- **Fixtures**: Several JSON fixtures available in `fixtures/` directory for development data
- **Static Files**: Admin customizations in `static/admin/css/custom_admin.css`
- **Logging**: Structured logging configured with JSON output to `logs/learning_platform.json`
- **CORS**: Pre-configured for React client on localhost:3000, localhost:5173, and production domains

## Client Integration

This API works with a companion React client. The GitHub OAuth flow redirects to `http://localhost:3000/auth/github` for local development.

## Production Considerations

- Uses Gunicorn for WSGI server
- Docker configuration available
- Nginx configuration templates in `config/`
- Structured logging with Logstash integration configured
- Service configuration for systemd deployment