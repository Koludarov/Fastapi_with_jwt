import redis
import uvicorn
from fastapi import FastAPI

from src.api.v1.resources import reshresh
from src.api.v1.resources import login
from src.api.v1.resources import logout
from src.api.v1.resources import logout_all
from src.api.v1.resources import users
from src.api.v1.resources import posts
from src.core import config
from src.db import cache, redis_cache
from src.db.db import database

app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=config.PROJECT_NAME,
    version=config.VERSION,
    # Адрес документации в красивом интерфейсе
    docs_url="/api/openapi",
    redoc_url="/api/redoc",
    # Адрес документации в формате OpenAPI
    openapi_url="/api/openapi.json",
)


@app.get("/")
def root():
    return {"service": config.PROJECT_NAME, "version": config.VERSION}


@app.on_event("startup")
async def startup():
    """Подключаемся к базам при старте сервера"""
    cache.cache = redis_cache.CacheRedis(
        cache_instance=redis.Redis(
            host=config.REDIS_HOST, port=config.REDIS_PORT, max_connections=10
        )
    )
    cache.cache1 = redis_cache.CacheRedis(cache_instance=redis.Redis(
        host=config.REDIS_HOST, port=config.REDIS_PORT, db=1, decode_responses=True,
    ))
    cache.cache2 = redis_cache.CacheRedis(cache_instance=redis.Redis(
        host=config.REDIS_HOST, port=config.REDIS_PORT, db=2, decode_responses=True,
    ))
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Отключаемся от баз при выключении сервера"""
    cache.cache.close()
    await database.disconnect()


# Подключаем роутеры к серверу
app.include_router(router=posts.router, prefix="/api/v1/posts")
app.include_router(router=users.router, prefix="/api/v1/users")
app.include_router(router=reshresh.router, prefix="/api/v1/refresh")
app.include_router(router=login.router, prefix="/api/v1/login")
app.include_router(router=logout.router, prefix="/api/v1/logout")
app.include_router(router=logout_all.router, prefix="/api/v1/logout_all")


if __name__ == "__main__":
    # Приложение может запускаться командой
    # `uvicorn main:app --host 0.0.0.0 --port 8000`
    # но чтобы не терять возможность использовать дебагер,
    # запустим uvicorn сервер через python
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
