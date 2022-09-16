import os

dsn = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", 5432)),
}
es_settings = {
    "es_api_path": os.environ.get("ES_API_PATH", "http://127.0.0.1:9200/"),
}

redis_host = os.environ.get("REDIS_HOST", "localhost")
