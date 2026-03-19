from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import guides, pages, users, auth, screenshot_v2

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(guides.router, prefix=f"{settings.API_V1_STR}/guides", tags=["guides"])
app.include_router(pages.router, prefix=f"{settings.API_V1_STR}/pages", tags=["pages"])
app.include_router(screenshot_v2.router)

@app.get("/")
def root():
    return {"message": "OnboardKit API", "version": settings.VERSION}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
