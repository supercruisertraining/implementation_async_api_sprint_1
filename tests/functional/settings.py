from pydantic import BaseSettings, RedisDsn


class TestSettings(BaseSettings):
    api_base_url = "http://127.0.0.1:8000"
    es_host_url: str = "http://127.0.0.1:9200"
    redis_dsn: RedisDsn = "redis://user:pass@127.0.0.1:6379/2"

    es_movies_index: str = "test_movies"
    es_persons_index: str = "test_persons"
    es_genres_index: str = "test_genres"

    es_movies_index_mapping_file: str = "./es_index_movies.json"
    es_persons_index_mapping_file: str = "./es_index_persons.json"
    es_genres_index_mapping_file: str = "./es_index_genres.json"


test_settings = TestSettings()
