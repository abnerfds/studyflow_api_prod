# Ferramentas do SQLAlchemy para lidar com chamadas não-bloqueantes (assíncronas)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Importa as variáveis do .env (Padrão 12-Factor App de segurança)
from config import settings

# Motor de conexão. echo=True faz o print das queries no terminal (útil para debug)
engine = create_async_engine(settings.database_url, echo=True)

# Fábrica de transações. expire_on_commit=False é essencial no async para os objetos
# não sumirem da memória após o commit no banco.
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Classe mãe que nossos models vão herdar para serem reconhecidos como tabelas
Base = declarative_base()


# Gerador de injeção de dependência. Abre e fecha a conexão do banco a cada requisição HTTP.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
