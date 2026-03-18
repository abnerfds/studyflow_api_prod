import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from config import Settings  # Importa sua classe de configuração
from database import Base

# Importações do seu projeto

# Objeto de configuração do Alembic
config = context.config

# Configura o log se o arquivo .ini existir
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define os metadados para que o 'autogenerate' detecte suas tabelas
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa migrações em modo 'offline'."""
    # Injeta a URL da sua classe Settings aqui
    url = Settings().database_url  # type: ignore

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configura o contexto da migração com a conexão ativa."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Cria o engine assíncrono injetando a URL de configuração."""

    # Captura a seção de configuração do alembic.ini
    section = config.get_section(config.config_ini_section, {})

    # Sobrescreve a URL do .ini pela URL real do seu Settings
    section["sqlalchemy.url"] = Settings().database_url  # type: ignore

    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Executa migrações em modo 'online'."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
