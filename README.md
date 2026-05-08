# Telegram Cleanup API

A clean, professional REST API for Telegram account cleanup. Built on FastAPI with the [telegram-cleanup](https://github.com/thirdbase1/Telegram-cleanup) SDK.

## Features

- **14 REST endpoints** — auth, analysis, cleanup, export
- **Auto-generated Swagger docs** at `/docs`
- **Full type validation** with Pydantic
- **CORS enabled** for frontend integration
- **Session isolation** per user
- **Privacy-first** — logout wipes all data

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API_ID and API_HASH

# Run the server
python run.py
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/phone` | Send login code |
| POST | `/api/v1/auth/login/code` | Verify code |
| POST | `/api/v1/auth/login/2fa` | Verify 2FA |
| GET | `/api/v1/auth/status` | Session status |
| POST | `/api/v1/auth/logout` | Logout & wipe |
| GET | `/api/v1/analysis/whitelist` | Get whitelist |
| POST | `/api/v1/analysis/whitelist` | Update whitelist |
| POST | `/api/v1/analysis/analyze` | Analyze account |
| GET | `/api/v1/analysis/preview` | Cleanup preview |
| POST | `/api/v1/cleanup/start` | Start cleanup |
| GET | `/api/v1/cleanup/progress` | Track progress |
| GET | `/api/v1/cleanup/result` | Final results |
| POST | `/api/v1/export/data` | Export JSON |
| GET | `/api/v1/export/download` | Download export |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_ID` | Yes | Telegram API ID |
| `API_HASH` | Yes | Telegram API hash |
| `CORS_ORIGINS` | No | Allowed origins (default: `*`) |

## Project Structure

```
├── main.py              # FastAPI app setup
├── run.py               # Server entry point
├── requirements.txt     # Dependencies
├── models/
│   └── schemas.py       # Pydantic models
├── routers/
│   ├── auth.py          # Authentication endpoints
│   ├── analysis.py      # Analysis endpoints
│   ├── cleanup.py       # Cleanup endpoints
│   └── export.py        # Export endpoints
└── services/
    ├── session_manager.py  # User session management
    └── cleanup_service.py  # Cleanup orchestration
```
