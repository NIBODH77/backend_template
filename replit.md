# RAMAERA Hosting Platform API

## Overview
This is a FastAPI-based backend API for the RAMAERA Hosting Platform. It provides endpoints for managing hosting services, billing, invoices, servers, user authentication, and more.

**Project Type:** Backend API (FastAPI + PostgreSQL)  
**Version:** 1.0.0  
**Status:** Running on Replit

## Tech Stack
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn (ASGI server)
- **Database:** PostgreSQL (AsyncPG driver)
- **ORM:** SQLAlchemy 2.0.23 (Async)
- **Migrations:** Alembic 1.12.1
- **Authentication:** JWT (python-jose)
- **Password Hashing:** Bcrypt + Passlib

## Project Structure
```
app/
├── api/v1/
│   ├── endpoints/      # API route handlers
│   │   ├── auth.py     # Authentication endpoints
│   │   ├── billing.py  # Billing management
│   │   ├── invoices.py # Invoice management
│   │   ├── orders.py   # Order management
│   │   ├── plans.py    # Hosting plans
│   │   ├── servers.py  # Server management
│   │   └── ...
│   └── api.py         # API router aggregation
├── core/
│   ├── config.py      # Application settings
│   ├── database.py    # Database connection
│   └── security.py    # Security utilities
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── services/          # Business logic layer
└── utils/             # Helper utilities

alembic/               # Database migrations
tests/                 # Test files
```

## API Endpoints
- **Root:** `GET /` - API information
- **Health Check:** `GET /health` - Server health status
- **API Docs:** `GET /docs` - Interactive Swagger UI
- **ReDoc:** `GET /redoc` - Alternative API documentation
- **API Routes:** `/api/v1/*` - All versioned API endpoints

## Recent Changes (Replit Setup)
- **2024-11-11:** Initial Replit setup
  - Installed Python 3.11 and all dependencies
  - Configured PostgreSQL database with AsyncPG
  - Updated CORS and allowed hosts for Replit's proxy environment
  - Fixed database URL handling (auto-converts to asyncpg and removes unsupported sslmode parameter)
  - Added SQLite fallback support for local testing (uses aiosqlite)
  - Applied database migrations (initial_tables)
  - Configured backend to run on localhost:8000
  - Moved Razorpay API keys to environment variables for security
  - Fixed model relationships (removed non-existent PaymentModel and SubscriptionModel references)

## Configuration
The application uses environment variables for configuration:
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Replit)
- `SECRET_KEY` - JWT secret key (set to default, should be changed in production)
- `RAZORPAY_KEY_ID` - Razorpay API key ID
- `RAZORPAY_KEY_SECRET` - Razorpay API secret

## Database
- Uses Replit's built-in PostgreSQL database (Neon-backed)
- Async SQLAlchemy with AsyncPG driver
- Migrations managed by Alembic
- Initial schema includes tables for: users, plans, servers, orders, invoices, billing, referrals, support tickets, and settings

## Running the Application
The application runs automatically via the configured workflow:
- **Command:** `python -m uvicorn app.main:app --host localhost --port 8000 --reload`
- **Port:** 8000 (backend only, not exposed to public)
- **Auto-reload:** Enabled for development

## Database Migrations
Run migrations with:
```bash
alembic upgrade head
```

Create new migration:
```bash
alembic revision --autogenerate -m "description"
```

## Development Notes
- The backend is configured to run on `localhost:8000` (not publicly accessible)
- CORS is configured to allow all origins for Replit's proxy environment
- TrustedHost middleware allows all hosts to work with Replit's iframe preview
- The API uses async/await patterns throughout for better performance
- All database operations are asynchronous

## Security Notes
- Change `SECRET_KEY` in production
- Razorpay API keys are stored in environment variables
- Default admin email: admin@ramaera.com
- JWT tokens expire after 30 minutes

## Testing
Test basic functionality:
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

Access API documentation at `/docs` or `/redoc`
