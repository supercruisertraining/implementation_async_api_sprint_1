import uuid
from abc import abstractmethod
from datetime import datetime
from typing import Union

from config.settings import redis_host
from redis import Redis


class BaseStateProvider:
    @abstractmethod
    def fetch_data(self) -> dict:
        pass

    @abstractmethod
    def update_data(self, data: dict) -> None:
        pass


class RedisStateProvider(BaseStateProvider):
    def __init__(self):
        self.redis_client: Redis = Redis(host=redis_host)

    def fetch_data(self) -> dict:
        return {k.decode("utf-8"): v.decode("utf-8") for k, v in self.redis_client.hgetall("state").items()}

    def update_data(self, data: dict) -> None:
        self.redis_client.hset("state", mapping=data)


class State:
    def __init__(self, state_provider: BaseStateProvider = RedisStateProvider()):
        self.state_provider = state_provider

    def get_state(self) -> dict:
        data: dict = self.state_provider.fetch_data()
        return {
            "last_id": str(data.get("last_id", "0" * 32)),
            "last_process_datetime": data.get("last_process_datetime", "0001-01-01 00:00:00"),
            "next_process_datetime": data.get("next_process_datetime", "0001-01-01 00:00:00"),
        }

    def set_state(
        self,
        last_id: Union[str, uuid.UUID, None],
        last_process_datetime: Union[str, datetime, None] = None,
        next_process_datetime: Union[str, datetime, None] = None,
    ) -> None:
        if last_id is None and last_process_datetime is None and next_process_datetime is None:
            return
        data = dict()
        if last_id is not None:
            data.update({"last_id": str(last_id)})
        if last_process_datetime is not None:
            data.update({"last_process_datetime": str(last_process_datetime)})
        if next_process_datetime is not None:
            data.update({"next_process_datetime": str(next_process_datetime)})
        self.state_provider.update_data(data)
