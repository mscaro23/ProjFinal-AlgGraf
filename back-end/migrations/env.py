from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool, MetaData
from dotenv import load_dotenv
from alembic import context

# Adiciona o diretório raiz ao sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importa Base ANTES dos modelos
from db.base import Base
from db.engine import DATABASE_URL

# Importa TODOS os modelos para que sejam detectados
from db import db_models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


class AlembicRunner:
    def __init__(
        self,
        metadata: MetaData,
        db_url: str,
    ):
        self.metadata = metadata
        # Alembic Config object, which provides
        # access to the values within the .ini file in use.
        self.config = context.config
        self.config.set_main_option("sqlalchemy.url", db_url)
        self.set_logging()

    def set_logging(self):
        # Interpret the config file for Python logging.
        if self.config.config_file_name is not None:
            fileConfig(self.config.config_file_name)

    def run_migrations_offline(self) -> None:
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a DBAPI to be available.

        Calls to context.execute() here emit the given string to the
        script output.

        """
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=self.metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online(self) -> None:
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=self.metadata)

            with context.begin_transaction():
                context.run_migrations()

    def run(self):
        """Run the Alembic migrations."""
        if context.is_offline_mode():
            self.run_migrations_offline()
        else:
            self.run_migrations_online()


alembic_runner = AlembicRunner(
    metadata=db_models.Base.metadata,
    db_url=DATABASE_URL,
)

alembic_runner.run()
