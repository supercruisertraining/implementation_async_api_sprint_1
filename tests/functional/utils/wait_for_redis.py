import time

from tests.functional.settings import test_settings

from redis import Redis

if __name__ == '__main__':
    redis = Redis(host=test_settings.redis_host)
    while True:
        if redis.ping():
            redis.close()
            break
        time.sleep(1)
