from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.routers import auth, companies, branches, users, roles, dashboard, ai_assistant

app = FastAPI(
    title="Nexus ERP API",
    description="Multi-company ERP suite — Login & Company Setup, Dashboard, and AI Assistant modules.",
    version="2.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Validation failed"},
    )


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "nexus-erp-api", "version": "2.4.0"}


app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(branches.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(dashboard.router)
app.include_router(ai_assistant.router)
