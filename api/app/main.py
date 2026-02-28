from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.routers import auth, ipr, compromisos, problemas, alertas, dashboard, catalogs
from app.routers import dgi_cockpit, dgi_initiatives, dgi_data, dgi_reports
from app.routers import presupuesto, convenios, admin, reuniones
from app.routers import search, actos

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title="GORE_OS API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

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

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
