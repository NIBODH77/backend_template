from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base
import asyncio
from sqlalchemy.engine import URL



# # Create database tables
# Base.metadata.create_all(bind=engine)






app = FastAPI(
    title=settings.PROJECT_NAME,
    description="RAMAERA Hosting Platform Backend API",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Add exception handlers



# ✅ Define your async DB initialization
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# # ✅ Run it once when the app starts
# @app.on_event("startup")
# async def on_startup():
#     await init_models()


@app.get("/")
async def root():
    return {
        "message": "RAMAERA Hosting Platform API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=settings.DEBUG
    
    )





@app.on_event("startup")
async def on_startup():
    # Print the connected database URL safely (without password)
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

    # Optionally, ensure all models are created
    await init_models()
    print("📦 Tables initialized (if not already present).")
