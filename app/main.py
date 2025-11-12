from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.responses import FileResponse
from sqlalchemy.engine import URL

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="RAMAERA Hosting Platform Backend API",
    version=settings.VERSION,
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Database initialization
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    print("🔗 Database connection check...")
    url = engine.url
    safe_url = URL.create(
        drivername=url.drivername,
        username=url.username,
        host=url.host,
        port=url.port,
        database=url.database
    )
    print(f"✅ Connected to database: {safe_url}")
    await init_models()
    print("📦 Tables initialized (if not already present).")

# Root and health check endpoints
@app.get("/")
async def root():
    return {
        "message": "RAMAERA Hosting Platform API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Endpoint for testing payment page
@app.get("/test-payment", response_class=FileResponse)
async def get_test_payment_page():
    return "test_payment.html"

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=settings.DEBUG
    )