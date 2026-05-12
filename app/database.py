from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings
from app.security import hash_password


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables() -> None:
    from app import models

    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_columns()
    _ensure_admin_user(models.User)


def _migrate_sqlite_columns() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    column_map = {
        "inventory_items": {
            "category": "VARCHAR(80) NOT NULL DEFAULT 'Geral'",
            "location": "VARCHAR(80) NOT NULL DEFAULT 'Almoxarifado'",
        },
        "withdrawals": {
            "companion_name": "VARCHAR(120)",
            "destination": "VARCHAR(160)",
        },
    }

    with engine.begin() as connection:
        for table_name, columns in column_map.items():
            if table_name not in table_names:
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, ddl in columns.items():
                if column_name not in existing:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))


def _ensure_admin_user(user_model: type) -> None:
    with SessionLocal() as db:
        has_users = db.query(user_model).first()
        if has_users:
            return

        settings = get_settings()
        db.add(
            user_model(
                username=settings.admin_username,
                full_name="Administrador",
                password_hash=hash_password(settings.admin_password),
                role="admin",
                active=True,
            )
        )
        db.commit()
