# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements*.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Run migrations
RUN python manage.py migrate

# Expose port
EXPOSE 8000

# Create logs directory if it doesn't exist
# RUN mkdir -p logs

# Start server
CMD ["gunicorn", "runsync.asgi:application", "--bind", "0.0.0.0:8000", "--log-level", "debug", "--access-logfile", "logs/runsync-access.log", "--error-logfile", "logs/runsync-error.log"] 