import time

import psycopg2
import requests


def backoff(start_sleep_time: float = 0.1, factor: int = 2, border_sleep_time: int = 10):
    def func_wrapper(func):
        def inner(*args, **kwargs):
            t = start_sleep_time
            for n in range(100):
                t = start_sleep_time * (factor**n) if t < border_sleep_time else border_sleep_time
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.ConnectionError:
                    time.sleep(t)
                except psycopg2.OperationalError:
                    time.sleep(t)
                except Exception as e:
                    raise Exception(f"Something was wrong: {str(e)}")

        return inner

    return func_wrapper
