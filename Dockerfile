FROM python:3.8-slim-buster

WORKDIR /app
COPY ./es_index_genres.json /app/
COPY ./es_index_movies.json /app/
COPY ./es_index_persons.json /app/
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./etl /app/etl/

COPY ./tests /app/tests/
COPY ./src /app/src/