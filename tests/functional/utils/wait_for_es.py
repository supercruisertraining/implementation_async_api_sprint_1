import time
import sys
import os
print(os.getcwd())
print(sys.path)
from tests.functional.settings import test_settings

from elasticsearch import Elasticsearch

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            es_client.close()
            break
        time.sleep(1)
