from urllib.parse import urljoin

import requests

from postgres_to_es.utils.backoff import backoff
from state.state_manager import State


class ESPusher:
    def __init__(self, es_api_path: str, es_index_name: str, state_adapter: State):
        self._state_adapter = state_adapter
        self.api_path = es_api_path
        self.index_name = es_index_name

    @backoff()
    def push_data(self, data_list: list) -> int:
        url = urljoin(self.api_path, "_bulk")
        res_data_list = []
        for data_element in data_list:
            res_data_list.append({"index": {"_index": self.index_name, "_id": data_element["id"]}})
            res_data_list.append(data_element)
        res_data_str = "\n".join(str(x).replace("'", '"') for x in res_data_list) + "\n"
        res = requests.post(url, data=res_data_str.encode("utf-8"), headers={"Content-Type": "application/json"})
        return res.status_code
