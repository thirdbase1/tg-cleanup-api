# Telegram Cleanup API

A clean, professional REST API for Telegram account cleanup, built on FastAPI with the telegram-cleanup SDK.

## Features

- **🔐 Secure Authentication** — Phone + Code + 2FA authentication flow
- **📊 Smart Analysis** — Scan chats, detect spam, estimate cleanup time  
- **🎯 Flexible Whitelist** — Keep important chats by username, link, or ID
- **🧹 Full Cleanup** — Leave channels/groups, block bots, delete private chats
- **💾 Data Export** — Backup your chat data as JSON before deletion
- **📈 Progress Tracking** — Real-time cleanup progress monitoring
- **🔒 Privacy First** — One-click logout wipes all session data

## Quick Start

### 1. Install Dependencies
```bash
cd api
pip install -r requirements.txt
```

### 2. Set Up Environment
Copy `.env.example` to `.env` and configure your Telegram API credentials:
```ini
API_ID=1234567
API_HASH=a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4
```

### 3. Start the API Server
```bash
python -m api.run
```

The API will be available at:
- **API**: http://localhost:8000/api/v1
- **Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## API Workflow

### Step 1: Authentication
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/phone" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'
```

### Step 2: Verify Code
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/code" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "code": "12345"}'
```

### Step 3: Set Whitelist (Optional)
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/whitelist" \
  -H "Content-Type: application/json" \
  -d '{"items": ["@MyFriend", "t.me/ImportantChannel"], "mode": "add"}'
```

### Step 4: Analyze Account
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json"
```

### Step 5: Start Cleanup
```bash
curl -X POST "http://localhost:8000/api/v1/cleanup/start" \
  -H "Content-Type: application/json"
```

### Step 6: Track Progress
```bash
curl -X GET "http://localhost:8000/api/v1/cleanup/progress"
```

### Step 7: Get Results
```bash
curl -X GET "http://localhost:8000/api/v1/cleanup/result"
```

### Step 8: Logout & Wipe Data
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout"
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/phone` - Send login code
- `POST /api/v1/auth/login/code` - Verify code
- `POST /api/v1/auth/login/2fa` - Verify 2FA password  
- `GET /api/v1/auth/status` - Check session status
- `POST /api/v1/auth/logout` - Logout & wipe data

### Analysis & Preview
- `GET /api/v1/analysis/whitelist` - Get current whitelist
- `POST /api/v1/analysis/whitelist` - Update whitelist
- `POST /api/v1/analysis/analyze` - Analyze account
- `GET /api/v1/analysis/preview` - Get cleanup preview

### Cleanup
- `POST /api/v1/cleanup/start` - Start cleanup process
- `GET /api/v1/cleanup/progress` - Track progress
- `GET /api/v1/cleanup/result` - Get final results

### Export
- `POST /api/v1/export/data` - Export data to JSON
- `GET /api/v1/export/download` - Download exported file

## Response Models

### Login Flow
```json
// Step 1: Send Code
{
  "status": "code_sent",
  "phone": "+1234567890"
}

// Step 2: Verify Code  
{
  "status": "authenticated",
  "phone": "+1234****90"
}
```

### Analysis
```json
{
  "total_chats": 150,
  "whitelisted": 20,
  "to_remove": 130,
  "spam_bots_detected": 15,
  "estimated_time": "~3 minutes",
  "activity": {
    "total": 150,
    "inactive_7d": 25,
    "inactive_30d": 45,
    "inactive_90d": 65
  }
}
```

### Progress
```json
{
  "processed": 45,
  "total": 130,
  "percentage": 34.6,
  "current_speed": 3,
  "recent_logs": [
    "🚪 Left group: Random Spam Group",
    "⛔ Blocked and deleted bot: @CryptoScamBot"
  ]
}
```

## Security & Privacy

- **Session Isolation**: Each user gets a unique session ID
- **Temporary Storage**: Sessions are deleted on logout
- **No Password Access**: Uses Telegram's official MTProto login
- **Data Wiping**: One-click logout removes all session files
- **Rate Limiting**: Built-in protection against Telegram API limits

## Architecture

```
api/
├── main.py              # FastAPI app & entry point
├── run.py               # Server runner
├── requirements.txt     # Dependencies
├── models/              # Pydantic schemas
│   └── schemas.py
├── routers/             # API route handlers
│   ├── auth.py
│   ├── analysis.py
│   ├── cleanup.py
│   └── export.py
└── services/            # Business logic
    ├── session_manager.py
    └── cleanup_service.py
```

## Error Handling

All endpoints return standardized error responses:
```json
{
  "error": "validation_error",
  "detail": "Invalid phone number format"
}
```

## Testing

The API can be tested using curl or any HTTP client. Start the server and visit `/docs` for interactive API documentation.

## Deployment

The API is production-ready with:
- Uvicicorn ASGI server
- CORS middleware for cross-origin requests
- Comprehensive OpenAPI documentation
- Graceful error handling
- Session management and cleanup

---

Built on top of the [telegram-cleanup](../) SDK with ❤️ for privacy-first Telegram management.