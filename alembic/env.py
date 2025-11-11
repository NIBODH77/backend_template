# # from logging.config import fileConfig

# # from sqlalchemy import engine_from_config
# # from sqlalchemy import pool

# # from alembic import context

# # # this is the Alembic Config object, which provides
# # # access to the values within the .ini file in use.
# # config = context.config

# # # Interpret the config file for Python logging.
# # # This line sets up loggers basically.
# # if config.config_file_name is not None:
# #     fileConfig(config.config_file_name)

# # # add your model's MetaData object here
# # # for 'autogenerate' support
# # # from myapp import mymodel
# # # target_metadata = mymodel.Base.metadata
# # target_metadata = None

# # # other values from the config, defined by the needs of env.py,
# # # can be acquired:
# # # my_important_option = config.get_main_option("my_important_option")
# # # ... etc.


# # def run_migrations_offline() -> None:
# #     """Run migrations in 'offline' mode.

# #     This configures the context with just a URL
# #     and not an Engine, though an Engine is acceptable
# #     here as well.  By skipping the Engine creation
# #     we don't even need a DBAPI to be available.

# #     Calls to context.execute() here emit the given string to the
# #     script output.

# #     """
# #     url = config.get_main_option("sqlalchemy.url")
# #     context.configure(
# #         url=url,
# #         target_metadata=target_metadata,
# #         literal_binds=True,
# #         dialect_opts={"paramstyle": "named"},
# #     )

# #     with context.begin_transaction():
# #         context.run_migrations()


# # def run_migrations_online() -> None:
# #     """Run migrations in 'online' mode.

# #     In this scenario we need to create an Engine
# #     and associate a connection with the context.

# #     """
# #     connectable = engine_from_config(
# #         config.get_section(config.config_ini_section, {}),
# #         prefix="sqlalchemy.",
# #         poolclass=pool.NullPool,
# #     )

# #     with connectable.connect() as connection:
# #         context.configure(
# #             connection=connection, target_metadata=target_metadata
# #         )

# #         with context.begin_transaction():
# #             context.run_migrations()


# # if context.is_offline_mode():
# #     run_migrations_offline()
# # else:
# #     run_migrations_online()







# import asyncio
# import os
# import sys
# from logging.config import fileConfig

# from sqlalchemy import create_engine, pool
# from sqlalchemy.engine import Connection
# from sqlalchemy.ext.asyncio import async_engine_from_config

# from alembic import context

# # Load environment variables

# from dotenv import load_dotenv
# # from app.models.models import Base


# from app.models.base import Base


# load_dotenv()

# # Add your project directory to Python path
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# config = context.config


# if config.config_file_name and os.path.exists(config.config_file_name):
#     try:
#         fileConfig(config.config_file_name)
#         print("✅ Logging configured successfully")
#     except Exception as e:
#         print(f"❌ Error configuring logging: {e}")
#     # fileConfig(config.config_file_name)


# sync_url=os.getenv("DATABASE_URL").replace("+asyncpg","")

# tartget_metadata = Base.metadata
# def run_migrations_offline() -> None:
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=tartget_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#         compare_type=True,  # To detect column type changes
#         compare_server_default=True
#     )
#     with context.begin_transaction():
#         context.run_migrations()

# def do_run_migrations(connection: Connection) -> None:
#     context.configure(
#         connection=connection, 
#         target_metadata=tartget_metadata
#     )
#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online() -> None:

#     connectable = create_engine(sync_url, poolclass=pool.NullPool)

 
#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, 
#             target_metadata=tartget_metadata,
#             compare_type=True,  # To detect column type changes
#             compare_server_default=True
#         )
#         with context.begin_transaction():
#             context.run_migrations()

# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()


import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection
from alembic import context
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ Ensure project root is in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# ✅ Alembic Config object
config = context.config

# ✅ Configure logging
if config.config_file_name and os.path.exists(config.config_file_name):
    try:
        fileConfig(config.config_file_name)
        print("✅ Logging configured successfully")
    except Exception as e:
        print(f"❌ Error configuring logging: {e}")

# ✅ Import Base AFTER sys.path is updated
from app.models.base import Base

# ✅ FIXED spelling mistake (was `tartget_metadata`)
target_metadata = Base.metadata

# ✅ Use SQLite for local development (same as database.py)
sync_url = "sqlite:///./ramaera_hosting.db"

# Override the sqlalchemy.url in alembic.ini
config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(sync_url, poolclass=pool.NullPool)
    
    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()lace("+asyncpg", "")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = sync_url or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(sync_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()



