import os
from logging import config as logging_config

from pydantic import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Config(BaseSettings):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_NAME: str = "movies"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    ELASTIC_HOST: str = "localhost"
    ELASTIC_PORT: int = 9200
