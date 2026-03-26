# NFC Reader System

Built with Django + Next.js + ACR122U

## Environment Setup (Production-Ready)

1. Copy env templates:

```bash
cp .env.example .env
cp nfc_backend/.env.example nfc_backend/.env
cp nfc_frontend/.env.example nfc_frontend/.env.local
cp nfc_agent/.env.example nfc_agent/.env
```

2. Update secrets and domains before production:

- Set `DJANGO_SECRET_KEY` to a strong random value.
- Set `DJANGO_DEBUG=False`.
- Set `DJANGO_ALLOWED_HOSTS` to your real domain/IPs.
- Set `DJANGO_CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to your frontend URL.
- Set `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_WS_URL` to public backend endpoints.

## Quick Start

### Backend
```bash
cd nfc_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd nfc_frontend
npm install
npm run dev
```

### NFC Agent
```bash
cd nfc_agent
pip install -r requirements.txt
python nfc_agent.py
```

## Docker Compose

```bash
cp .env.example .env
docker compose up --build -d
```

Useful commands:

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose down
```

Notes:

- Backend waits for migrations at startup and serves ASGI via Daphne.
- Frontend starts only after backend healthcheck passes.
- SQLite is persisted in Docker volume `backend_data`.

Visit `http://localhost:3000` to view the dashboard.
