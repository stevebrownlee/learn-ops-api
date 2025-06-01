# Comprehensive Logging Strategy for Learning Platform API

## Overview

This document outlines a comprehensive logging strategy for the Learning Platform API, with a particular focus on critical workflows such as student assignment to cohorts. The strategy uses structlog for structured logging and includes a solution for log aggregation, storage, and viewing through a public URL.

## Goals

- Implement consistent, structured logging across the entire application
- Provide detailed context for all log events
- Enable easy filtering and searching of logs
- Ensure critical workflows are well-documented in logs
- Make logs accessible through a public URL for authorized personnel
- Support both development and production environments

## Structlog Implementation

### 1. Installation and Dependencies

```bash
pip install structlog django-structlog elasticsearch logstash kibana
```

Add to requirements.txt:
```
structlog==23.1.0
django-structlog==5.0.0
python-json-logger==2.0.7
```

### 2. Configuration in Django Settings

```python
# settings.py

import structlog
import logging.config
import time

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/learning_platform.json",
            "formatter": "json_formatter",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        },
        "logstash": {
            "class": "logstash.TCPLogstashHandler",
            "host": "logstash",  # Docker service name or actual host
            "port": 5000,
            "version": 1,
            "message_type": "learning_platform",
            "fqdn": False,
            "tags": ["django", "learning_platform"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "json_file", "logstash"],
            "level": "INFO",
        },
        "LearningAPI": {
            "handlers": ["console", "json_file", "logstash"],
            "level": "DEBUG",
            "propagate": False,
        },
        "LearningAPI.cohort": {
            "handlers": ["console", "json_file", "logstash"],
            "level": "DEBUG",
            "propagate": False,
        },
        "LearningAPI.student": {
            "handlers": ["console", "json_file", "logstash"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### 3. Create a Logging Utility Module

```python
# LearningAPI/utils/logging.py

import structlog
from functools import wraps
import time
import uuid

# Get a logger instance
logger = structlog.get_logger("LearningAPI")

def get_logger(module_name):
    """Get a logger for a specific module"""
    return structlog.get_logger(f"LearningAPI.{module_name}")

def bind_request_context(logger, request):
    """Bind common request context to a logger"""
    user_id = getattr(request.auth, 'user_id', None) if hasattr(request, 'auth') else None
    username = getattr(request.auth.user, 'username', None) if hasattr(request, 'auth') and hasattr(request.auth, 'user') else None

    return logger.bind(
        request_id=str(uuid.uuid4()),
        user_id=user_id,
        username=username,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        path=request.path,
        method=request.method,
    )

def log_action(action_type):
    """Decorator to log actions with timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            module_name = self.__class__.__module__.split('.')[-1]
            action_logger = get_logger(module_name)
            action_logger = bind_request_context(action_logger, request)

            # Extract relevant IDs from kwargs or request
            pk = kwargs.get('pk')

            # Log the start of the action
            action_logger.info(
                f"{action_type}_started",
                view=self.__class__.__name__,
                action=func.__name__,
                pk=pk,
            )

            start_time = time.time()
            try:
                result = func(self, request, *args, **kwargs)

                # Log successful completion
                action_logger.info(
                    f"{action_type}_completed",
                    view=self.__class__.__name__,
                    action=func.__name__,
                    pk=pk,
                    duration_ms=int((time.time() - start_time) * 1000),
                    status_code=getattr(result, 'status_code', None),
                )
                return result
            except Exception as e:
                # Log exception
                action_logger.exception(
                    f"{action_type}_failed",
                    view=self.__class__.__name__,
                    action=func.__name__,
                    pk=pk,
                    duration_ms=int((time.time() - start_time) * 1000),
                    error=str(e),
                )
                raise
        return wrapper
    return decorator
```

## Specific Implementation for Cohort Assignment

### Modify CohortViewSet to Include Structured Logging

```python
# LearningAPI/views/cohort_view.py

from django.db.models import Count, Q
from django.db import IntegrityError
from django.http import HttpResponseServerError
from rest_framework import serializers, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.people import Cohort, NssUser, NssUserCohort, CohortInfo
from LearningAPI.models.coursework import CohortCourse, Course, Project, StudentProject
from LearningAPI.utils.logging import get_logger, bind_request_context, log_action

# Get module-specific logger
logger = get_logger("cohort")

class CohortPermission(permissions.BasePermission):
    """Cohort permissions"""

    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'destroy', 'assign', 'migrate', 'active']:
            return request.auth.user.is_staff
        elif view.action in ['retrieve', 'list']:
            return True
        else:
            return False


class CohortViewSet(ViewSet):
    """Cohort view set"""

    permission_classes = (CohortPermission,)

    @log_action("cohort_creation")
    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        # Existing implementation with added logging...

    @log_action("cohort_retrieval")
    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        # Existing implementation with added logging...

    @log_action("cohort_update")
    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        # Existing implementation with added logging...

    @log_action("cohort_deletion")
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 204, 404, or 500 status code
        """
        # Existing implementation with added logging...

    @log_action("cohort_listing")
    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        # Existing implementation with added logging...

    @log_action("cohort_activation")
    @action(methods=['put', ], detail=True)
    def active(self, request, pk):
        # Existing implementation with added logging...

    @log_action("cohort_migration")
    @action(methods=['put', ], detail=True)
    def migrate(self, request, pk):
        """Migrate all students in a cohort from client side to server side

        1. Assign all students in cohort to first book of chosen server-side course
        """
        # Existing implementation with added logging...

    @log_action("cohort_assignment")
    @action(methods=['post', 'delete'], detail=True)
    def assign(self, request, pk):
        """Assign student or instructor to an existing cohort"""

        # Get request-specific logger with context
        req_logger = bind_request_context(logger, request)

        if request.method == "POST":
            cohort = None
            member = None
            user_type = request.query_params.get("userType", None)

            req_logger.info(
                "cohort_assignment_started",
                cohort_id=pk,
                user_type=user_type
            )

            try:
                cohort = Cohort.objects.get(pk=pk)
                req_logger.debug("cohort_found", cohort_name=cohort.name)

                if user_type is not None and user_type == "instructor":
                    req_logger.info("instructor_assignment_attempt")
                    try:
                        member = NssUser.objects.get(user=request.auth.user)
                        req_logger.debug("instructor_found", instructor_id=member.id)

                        membership = NssUserCohort.objects.get(nss_user=member)
                        req_logger.warning(
                            "instructor_already_assigned",
                            current_cohort_id=membership.cohort.id,
                            current_cohort_name=membership.cohort.name
                        )

                        return Response(
                            {'message': f'Instructor cannot be in more than 1 cohort at a time. Currently assigned to cohort {membership.cohort.name}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except NssUserCohort.DoesNotExist:
                        req_logger.debug("instructor_not_assigned_to_any_cohort")
                        pass
                else:
                    user_id = int(request.data["person_id"])
                    req_logger.info("student_assignment_attempt", student_id=user_id)

                    member = NssUser.objects.get(pk=user_id)
                    req_logger.debug("student_found", student_id=member.id, student_name=member.full_name)

                # Check if already assigned
                NssUserCohort.objects.get(cohort=cohort, nss_user=member)
                req_logger.warning(
                    "user_already_assigned_to_cohort",
                    user_id=member.id,
                    cohort_id=cohort.id
                )

                return Response(
                    {'message': 'Person is already assigned to cohort'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except NssUserCohort.DoesNotExist:
                req_logger.info(
                    "creating_cohort_assignment",
                    user_id=member.id,
                    cohort_id=cohort.id
                )

                relationship = NssUserCohort()
                relationship.cohort = cohort
                relationship.nss_user = member
                relationship.save()

                req_logger.info(
                    "cohort_assignment_created",
                    user_id=member.id,
                    cohort_id=cohort.id,
                    relationship_id=relationship.id
                )

                if user_type is None:
                    # This is a student assignment
                    req_logger.info(
                        "assigning_student_to_first_project",
                        student_id=member.id,
                        cohort_id=cohort.id
                    )

                    try:
                        # Assign student to first project in cohort's active course
                        book_first_project = Project.objects.get(
                            index=0,
                            book__course=cohort.courses.get(active=True).course,
                            book__index=0
                        )

                        req_logger.debug(
                            "first_project_found",
                            project_id=book_first_project.id,
                            project_name=book_first_project.name
                        )

                        student_project = StudentProject()
                        student_project.student = member
                        student_project.project = book_first_project
                        student_project.save()

                        req_logger.info(
                            "student_assigned_to_project",
                            student_id=member.id,
                            project_id=book_first_project.id,
                            student_project_id=student_project.id
                        )
                    except Exception as ex:
                        req_logger.error(
                            "failed_to_assign_student_to_project",
                            student_id=member.id,
                            error=str(ex)
                        )
                        # Continue execution - we don't want to fail the cohort assignment
                        # if project assignment fails

            except Cohort.DoesNotExist as ex:
                req_logger.error(
                    "cohort_not_found",
                    cohort_id=pk,
                    error=str(ex)
                )
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except NssUser.DoesNotExist as ex:
                req_logger.error(
                    "user_not_found",
                    user_type=user_type,
                    user_id=request.data.get("person_id") if user_type is None else "current_user",
                    error=str(ex)
                )
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                req_logger.exception(
                    "unexpected_error_during_assignment",
                    error=str(ex)
                )
                return HttpResponseServerError(ex)

            req_logger.info(
                "cohort_assignment_completed",
                user_id=member.id,
                cohort_id=cohort.id,
                user_type=user_type if user_type else "student"
            )

            return Response({'message': 'User assigned to cohort'}, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            # Similar detailed logging for DELETE operation...
            # Existing implementation with added logging...

        return Response(
            {'message': 'Unsupported HTTP method'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
```

## Log Aggregation and Viewing Solution

### ELK Stack (Elasticsearch, Logstash, Kibana)

For a comprehensive logging solution with a public URL for viewing logs, we recommend implementing the ELK stack:

1. **Elasticsearch**: For storing and indexing logs
2. **Logstash**: For log processing and forwarding
3. **Kibana**: For log visualization and exploration

#### Docker Compose Setup

```yaml
# docker-compose.yml

version: '3'
services:
  # Your existing Django application
  web:
    build: .
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - elasticsearch
      - logstash
    environment:
      - DJANGO_SETTINGS_MODULE=LearningPlatform.settings

  # Elasticsearch for log storage and indexing
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  # Logstash for log processing
  logstash:
    image: docker.elastic.co/logstash/logstash:7.17.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch

  # Kibana for log visualization
  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_URL: http://elasticsearch:9200
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

#### Logstash Configuration

```
# logstash/pipeline/logstash.conf

input {
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  if [type] == "learning_platform" {
    mutate {
      add_field => { "[@metadata][index]" => "learning-platform-%{+YYYY.MM.dd}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][index]}"
  }
}
```

### Alternative: Cloud-Based Solutions

For a more managed approach with less infrastructure overhead, consider these cloud-based logging solutions:

1. **Datadog**:
   - Comprehensive monitoring and logging platform
   - Easy integration with Django
   - Public URL access with authentication

2. **New Relic**:
   - Application performance monitoring with logging
   - Good visualization tools
   - Secure public access

3. **Loggly**:
   - Cloud-based log management
   - Simple integration
   - Shareable dashboards

4. **AWS CloudWatch Logs**:
   - If already using AWS infrastructure
   - Can be integrated with Elasticsearch and Kibana
   - Access control through IAM

## Middleware for Request/Response Logging

Add a middleware to automatically log all requests and responses:

```python
# LearningAPI/middleware/logging_middleware.py

import structlog
import time
import uuid
from django.utils.deprecation import MiddlewareMixin

logger = structlog.get_logger("LearningAPI.http")

class StructlogMiddleware(MiddlewareMixin):
    """Middleware to log all requests and responses"""

    def process_request(self, request):
        request.id = str(uuid.uuid4())
        request.start_time = time.time()

        # Don't log static file requests
        if '/static/' in request.path or '/media/' in request.path:
            return None

        # Create a logger with request context
        request.logger = logger.bind(
            request_id=request.id,
            user_id=getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            path=request.path,
            method=request.method,
        )

        request.logger.info("request_started")
        return None

    def process_response(self, request, response):
        # Don't log static file responses
        if '/static/' in request.path or '/media/' in request.path:
            return response

        if hasattr(request, 'logger') and hasattr(request, 'start_time'):
            duration_ms = int((time.time() - request.start_time) * 1000)
            request.logger.info(
                "request_finished",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
        return response

    def process_exception(self, request, exception):
        if hasattr(request, 'logger'):
            request.logger.exception(
                "request_failed",
                error=str(exception),
            )
        return None
```

Add the middleware to your Django settings:

```python
# settings.py

MIDDLEWARE = [
    # ... other middleware
    'LearningAPI.middleware.logging_middleware.StructlogMiddleware',
    # ... other middleware
]
```

## Best Practices for Logging

1. **Log Levels**:
   - DEBUG: Detailed information for debugging
   - INFO: Confirmation that things are working as expected
   - WARNING: Indication that something unexpected happened
   - ERROR: Due to a more serious problem, the software couldn't perform some function
   - CRITICAL: A serious error indicating that the program itself may be unable to continue running

2. **What to Log**:
   - User actions (login, logout, permissions changes)
   - Data changes (create, update, delete)
   - System events (startup, shutdown, configuration changes)
   - Errors and exceptions
   - Performance metrics (response times, database query times)

3. **Context Information**:
   - User ID and username
   - Request ID (for tracing requests across services)
   - IP address
   - Timestamp
   - Action being performed
   - Relevant IDs (cohort ID, student ID, etc.)
   - Duration of operations

4. **Security Considerations**:
   - Never log sensitive information (passwords, tokens, PII)
   - Implement log rotation to manage disk space
   - Set up log retention policies
   - Ensure logs are stored securely
   - Implement access controls for log viewing

## Implementation Plan

1. **Phase 1: Basic Setup**
   - Install structlog and configure in Django settings
   - Create logging utility module
   - Implement middleware for request/response logging
   - Add basic logging to critical views

2. **Phase 2: ELK Stack Integration**
   - Set up Elasticsearch, Logstash, and Kibana
   - Configure Logstash to receive logs from Django
   - Create basic Kibana dashboards

3. **Phase 3: Comprehensive Logging**
   - Add detailed logging to all views
   - Create custom dashboards in Kibana
   - Set up alerts for critical errors

4. **Phase 4: Monitoring and Refinement**
   - Monitor log volume and performance impact
   - Refine logging levels and content
   - Create additional dashboards for specific use cases

## Conclusion

This comprehensive logging strategy provides a solid foundation for monitoring and debugging the Learning Platform API. By implementing structured logging with structlog and setting up the ELK stack for log aggregation and viewing, we can gain valuable insights into system behavior, track critical workflows like student assignment, and quickly identify and resolve issues.