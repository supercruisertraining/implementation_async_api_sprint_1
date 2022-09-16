import sys
import time
from datetime import datetime

from config.settings import dsn, es_settings

from postgres_to_es.data_consumer.data_consumer import PostgresLoader
from postgres_to_es.data_pusher.data_pusher import ESPusher
from state.state_manager import State

index_name = sys.argv[1]

state_adapter = State()
pg_client = PostgresLoader(index_name=index_name, dsn=dsn, state_adapter=state_adapter)
es_client = ESPusher(es_index_name=index_name, **es_settings, state_adapter=state_adapter)
while True:
    data = pg_client.load_actual_data()
    if data:
        while data:
            es_client.push_data(data)
            state_adapter.set_state(last_id=str(data[-1]["id"]))
            data = pg_client.load_actual_data()

        state_adapter.set_state(
            last_id="0" * 32,  # Это нулевое значение в uuid4
            last_process_datetime=state_adapter.get_state()["next_process_datetime"],
            next_process_datetime=datetime.now(),
        )
    print("Iteration Done")
    time.sleep(100)
