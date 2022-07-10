from contextlib import closing
from typing import Union

import psycopg2
from psycopg2.extras import RealDictCursor

from etl.postgres_to_es.data_consumer.sql_film_work import fetch_100_modified_movies, fetch_100_modified_genres, \
    fetch_100_modified_persons, fetch_persons, get_genre
from etl.postgres_to_es.utils.backoff import backoff
from etl.state.state_manager import State


class PostgresLoader:
    def __init__(self, index_name, dsn: dict, state_adapter: State):
        self.index_name = index_name
        self._dsn = dsn
        self._state_adapter = state_adapter

    @backoff()
    def load_actual_data(self) -> Union[list, None]:
        with closing(psycopg2.connect(**self._dsn, cursor_factory=RealDictCursor)) as pg_conn:
            state = self._state_adapter.get_state()
            last_id = state["last_id"]
            last_process_datetime = state["last_process_datetime"]
            if self.index_name == "movies":
                query = fetch_100_modified_movies(last_id=last_id, last_process_datetime=last_process_datetime)
            elif self.index_name == "genres":
                query = fetch_100_modified_genres(last_id=last_id, last_process_datetime=last_process_datetime)
            elif self.index_name == "persons":
                query = fetch_100_modified_persons(last_id=last_id, last_process_datetime=last_process_datetime)
            else:
                raise Exception("Unknown data type")
            with pg_conn.cursor() as cur:
                cur.execute(query)
                result_data_list = cur.fetchall()
            if not result_data_list:
                return None
            result_list = []
            for result_data_element in result_data_list:
                if self.index_name == "movies":
                    current_data = self._film_work_process(result_data_element, pg_conn)
                elif self.index_name == "genres":
                    current_data = self._genre_process(result_data_element, pg_conn)
                elif self.index_name == "persons":
                    current_data = self._person_processor(result_data_element, pg_conn)
                result_list.append(current_data)

            return result_list

    def _film_work_process(self, data_element, pg_conn):
        current_film_work_data = {
            "id": str(data_element["id"]),
            "rating": float(data_element["rating"]),
            "title": data_element["title"],
            "description": data_element["description"],
            "creation_date": str(data_element["creation_date"]),
            "genres": [],
            "directors": [],
            "writers": [],
            "actors": [],
        }
        with pg_conn.cursor() as cur:
            cur.execute(get_genre(str(data_element["id"])))
            current_film_work_data["genres"] = [{"id": genre["id"], "name": genre["name"]} for genre in cur.fetchall()]
            cur.execute(fetch_persons(str(data_element["id"])))
            for person in cur.fetchall() or []:
                if person["role"] == "director":
                    current_film_work_data["directors"].append({"id": person["id"], "full_name": person["full_name"]})
                elif person["role"] == "writer":
                    current_film_work_data["writers"].append({"id": person["id"], "full_name": person["full_name"]})
                elif person["role"] == "actor":
                    current_film_work_data["actors"].append({"id": person["id"], "full_name": person["full_name"]})
        return current_film_work_data

    def _genre_process(self, data_element, pg_conn=None):
        return {
            "id": str(data_element["id"]),
            "name": data_element["name"],
            "description": data_element["description"],
        }

    def _person_processor(self, data_element, pg_conn=None):
        return {
            "id": str(data_element["id"]),
            "full_name": data_element["full_name"],
        }
