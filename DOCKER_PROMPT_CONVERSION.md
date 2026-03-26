# DOCKER CONVERSION GUIDE & PROMPT

If you want to deploy this NFC project using Docker, follow these steps. This setup excludes the `nfc_agent` (since it should run on the client's local machine with the hardware device) and focuses on the **Backend** and **Frontend**.

### 1. Backend Dockerfile (`nfc_backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim

# Install system dependencies for pyscard and Daphne
RUN apt-get update && apt-get install -y \
    libpcsclite-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run entrypoint command (database migrations + daphne)
CMD python manage.py migrate && daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

### 2. Frontend Dockerfile (`nfc_frontend/Dockerfile`)
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
```

### 3. Docker Compose (`docker-compose.yml`)
Place this in the root (`NFC/`):
```yaml
version: '3.8'

services:
  backend:
    build: ./nfc_backend
    ports:
      - "8000:8000"
    volumes:
      - ./nfc_backend/db.sqlite3:/app/db.sqlite3
    environment:
      - DEBUG=True
      - ALLOWED_HOSTS=*

  frontend:
    build: ./nfc_frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

---

### PROMPT FOR DEPLOYMENT (Instruction to Assistant)
> "Please dockerize the NFC project. Create a multi-container setup using Docker Compose. The backend should run Django/Daphne on port 8000 and handle both REST and WebSockets. The frontend should be a production build of the Next.js app on port 3000. Ensure the database (db.sqlite3) is persisted via a volume. The NFCAgent is a standalone EXE and should not be included in the Docker containers."

### How to Build & Run:
1. Open terminal in the root folder.
2. Run: `docker-compose up --build`
3. Access Dashboard at: `http://localhost:3000`
4. NFCAgent (EXE) will connect to: `http://localhost:8000`
