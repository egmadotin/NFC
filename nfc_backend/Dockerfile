FROM python:3.11-slim

# Install system dependencies for pyscard and Daphne
RUN apt-get update && apt-get install -y \
    libpcsclite-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create virtual environment and update PATH
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements.txt and install
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=500 -r requirements.txt

# Copy project files
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.settings

# Expose port 8000
EXPOSE 8000

# Run migrations and start daphne
CMD ["sh", "-c", "python manage.py migrate --noinput && daphne -b 0.0.0.0 -p 8000 core.asgi:application"]
