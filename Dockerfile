FROM python:3.9

WORKDIR /app
COPY ./es_index_genres.json /app/
COPY ./es_index_movies.json /app/
COPY ./es_index_persons.json /app/
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./etl /app/etl/

COPY ./tests /app/tests/
COPY ./src /app/src/