import os
from logging import config as logging_config

from pydantic import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Config(BaseSettings):
    TEST: bool = True
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_NAME: str = "movies"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    ELASTIC_HOST: str = "localhost"
    ELASTIC_PORT: int = 9200
    es_movies_index: str = "movies"
    es_persons_index: str = "persons"
    es_genres_index: str = "genres"

    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"

    CHECK_PERMISSION_URL: str = "http://127.0.0.1:5000/admin/api/v1/check_permission"
    MIN_ROLE: str = "lite"

    LOGSTASH_HOST: str = "localhost"
    LOGSTASH_PORT: int = 5044
    LOGSTASH_TAG: str = "fast-api-app"


config = Config()
