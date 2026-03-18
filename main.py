from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from config import Settings
from database import Base, setup_database
from routers import candidates

_app: FastAPI | None = None
_app_database_url: str | None = None


def create_app() -> FastAPI:
    global _app, _app_database_url

    database_url = os.getenv("DATABASE_URL") or Settings().database_url  # type: ignore

    if _app is not None and _app_database_url == database_url:
        return _app

    engine, session_factory = setup_database(database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield

        await engine.dispose()

    app = FastAPI(
        title="StudyFlow API",
        description="RESTful API para gestão de estudos, seguindo o padrão Layered Architecture",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.engine = engine
    app.state.session_factory = session_factory

    Instrumentator().instrument(app).expose(app)
    app.include_router(candidates.router, prefix="/api/v1")
    _app = app
    _app_database_url = database_url
    return app


app = create_app()
