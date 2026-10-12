from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.middleware.security import SecurityHeadersMiddleware

from app.routers import auth, ipr, compromisos, problemas, alertas, dashboard, catalogs
from app.routers import dgi_data, convenios, admin, search, actos
from app.routers import dgi_processes, dgi_coordination, dgi_escalation, dgi_services, risk, notifications

settings = get_settings()


def create_app() -> FastAPI:
    is_dev = settings.ENV == "development"
    app = FastAPI(
        title="GORE_OS API",
        version="0.1.0",
        docs_url="/api/docs" if is_dev else None,
        openapi_url="/api/openapi.json" if is_dev else None,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    )

    app.include_router(auth.router)
    app.include_router(ipr.router)
    app.include_router(compromisos.router)
    app.include_router(problemas.router)
    app.include_router(alertas.router)
    app.include_router(dashboard.router)
    app.include_router(catalogs.router)
    app.include_router(dgi_data.router)
    app.include_router(convenios.router)
    app.include_router(admin.router)
    app.include_router(search.router)
    app.include_router(actos.router)
    app.include_router(dgi_processes.router)
    app.include_router(dgi_coordination.router)
    app.include_router(dgi_escalation.router)
    app.include_router(dgi_services.router)
    app.include_router(risk.router)
    app.include_router(notifications.router)

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
