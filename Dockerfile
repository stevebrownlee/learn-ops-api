# Use Python 3.11.11 as specified in Pipfile
FROM python:3.11.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --upgrade pip && \
  pip install pipenv

COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv (creates virtual environment)
RUN pipenv install --system --deploy --verbose

# Copy the entire application first
COPY . .

# Copy and make entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port 8000 (default for Django dev server)
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]