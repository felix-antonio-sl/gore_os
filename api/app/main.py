from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.middleware.security import SecurityHeadersMiddleware
from app.routers import auth, ipr, compromisos, problemas, alertas, dashboard, catalogs
from app.routers import dgi_cockpit, dgi_initiatives, dgi_data, dgi_reports
from app.routers import presupuesto, convenios, admin, reuniones
from app.routers import search, actos, core_sessions, dgi_cartera, dgi_bottleneck, dgi_processes

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
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(ipr.router)
    app.include_router(compromisos.router)
    app.include_router(problemas.router)
    app.include_router(alertas.router)
    app.include_router(dashboard.router)
    app.include_router(catalogs.router)
    app.include_router(dgi_cockpit.router)
    app.include_router(dgi_initiatives.router)
    app.include_router(dgi_data.router)
    app.include_router(dgi_reports.router)
    app.include_router(presupuesto.router)
    app.include_router(convenios.router)
    app.include_router(admin.router)
    app.include_router(reuniones.router)
    app.include_router(search.router)
    app.include_router(actos.router)
    app.include_router(core_sessions.router)
    app.include_router(dgi_cartera.router)
    app.include_router(dgi_bottleneck.router)
    app.include_router(dgi_processes.router)

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
