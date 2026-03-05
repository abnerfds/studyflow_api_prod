import pytest
import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from database import get_db, AsyncSessionLocal, engine

@pytest_asyncio.fixture(scope="function")
async def client():
    # Criamos uma nova sessão para o teste
    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    # Substituímos a dependência global da API pela do teste
    app.dependency_overrides[get_db] = override_get_db
    
    # O ASGITransport conecta o cliente diretamente ao loop do teste
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    # Limpamos tudo após o teste
    app.dependency_overrides.clear()
    # Importante: Fazemos o dispose do engine para não sobrar conexões de loops antigos
    await engine.dispose()