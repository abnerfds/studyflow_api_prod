from contextlib import asynccontextmanager

from fastapi import FastAPI

# Importamos a engine do banco para poder criar as tabelas ao iniciar
from database import Base, engine

# Importamos nosso "Controller" para registrar no servidor principal
from routers import candidates


# --- GESTÃO DE CICLO DE VIDA (Lifespan) ---
# Substitui os antigos eventos de startup/shutdown.
# Tudo antes do "yield" roda quando o servidor sobe. Tudo depois, quando ele desliga.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Abre uma transação isolada com o Postgres
    async with engine.begin() as conn:
        # Inspeciona nossos models.py e cria as tabelas "candidates", "disciplines", etc., se não existirem.
        # run_sync: Um utilitário para rodar operações síncronas de infraestrutura dentro do nosso fluxo assíncrono.
        await conn.run_sync(Base.metadata.create_all)

    # Libera a aplicação para rodar e receber conexões
    yield


# Inicialização limpa da aplicação principal.
# Estes metadados são o que alimentam a tela inicial do Swagger (/docs).
app = FastAPI(
    title="StudyFlow API",
    description="RESTful API para gestão de estudos, seguindo o padrão Layered Architecture",
    version="1.0.0",
    lifespan=lifespan,
)

# Registramos as rotas do arquivo candidates.py.
# include_router age como o "require" das rotas do Laravel.
# prefix="/api/v1": Prática de DevOps para versionar a API. O endpoint final vira POST /api/v1/candidates/
app.include_router(candidates.router, prefix="/api/v1")
