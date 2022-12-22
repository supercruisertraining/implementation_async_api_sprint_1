import logging

import aioredis
import logstash
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from core.config import config
from db import elastic, redis

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logstash_handler = logstash.LogstashHandler(host=config.LOGSTASH_HOST, port=config.LOGSTASH_PORT)
logger.addHandler(logstash_handler)

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = await aioredis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"],
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@app.middleware('http')
async def request_logger(request: Request, call_next):
    request_id = request.headers.get('X-Request-Id', "")
    logger.info(request.url, extra={'tag': config.LOGSTASH_TAG, "request_id": request_id})
    response = await call_next(request)
    return response


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
