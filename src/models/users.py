import sqlalchemy
from datetime import datetime

from src.db.db import metadata


__all__ = ("users",)

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column('email', sqlalchemy.String, unique=True),
    sqlalchemy.Column('username', sqlalchemy.String),
    sqlalchemy.Column('password', sqlalchemy.String),
    sqlalchemy.Column('uuid', sqlalchemy.String, unique=True),
    sqlalchemy.Column('is_superuser', sqlalchemy.Boolean, default=False),
    sqlalchemy.Column('roles', sqlalchemy.String, default='[]'),
    sqlalchemy.Column('is_totp_enabled', sqlalchemy.Boolean, default=False),
    sqlalchemy.Column('is_active', sqlalchemy.Boolean, default=True),
    sqlalchemy.Column('created_at', sqlalchemy.DateTime, default=datetime.utcnow),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime, default=datetime.utcnow),
)
