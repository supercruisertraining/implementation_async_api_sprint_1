from datetime import datetime


def fetch_100_modified_movies(last_id: str, last_process_datetime: datetime) -> str:
    return """
    SELECT
        f_w.id,
        f_w.title,
        f_w.description,
        f_w.rating,
        f_w.creation_date
    FROM content.film_work f_w
    JOIN content.genre_film_work g_f_w ON f_w.id = g_f_w.film_work_id
    JOIN content.genre g ON g.id = g_f_w.genre_id
    JOIN content.person_film_work p_f_w ON f_w.id = p_f_w.film_work_id
    JOIN content.person p ON p.id = p_f_w.person_id
    WHERE f_w.id > '{id_}'
    GROUP BY f_w.id
    HAVING f_w.modified > '{last_datetime_}' OR
           MAX(g_f_w.created) > '{last_datetime_}' OR
           MAX(g.modified) > '{last_datetime_}' OR
           MAX(p_f_w.created) > '{last_datetime_}' OR
           MAX(p.modified) > '{last_datetime_}'
    ORDER BY f_w.id
    LIMIT 100;
    """.format(
        id_=last_id, last_datetime_=last_process_datetime
    )


def fetch_100_modified_genres(last_id: str, last_process_datetime: datetime) -> str:
    return """
    SELECT id, name, description
    FROM content.genre
    WHERE id > '{id_}'
    AND modified > '{last_datetime_}'
    ORDER BY id
    LIMIT 100;
    """.format(
        id_=last_id, last_datetime_=last_process_datetime
    )


def fetch_100_modified_persons(last_id: str, last_process_datetime: datetime) -> str:
    return """
    SELECT id, full_name
    FROM content.person
    WHERE id > '{id_}'
    AND modified > '{last_datetime_}'
    ORDER BY id
    LIMIT 100;
    """.format(
        id_=last_id, last_datetime_=last_process_datetime
    )


def fetch_persons(film_work_id: str) -> str:
    query = """
        SELECT p.id, p.full_name, p_f_w.role
        FROM content.person p
        JOIN content.person_film_work p_f_w ON p_f_w.person_id = p.id
        WHERE p_f_w.film_work_id = '{id_}';
    """.format(
        id_=film_work_id
    )
    return query


def get_genre(film_work_id: str) -> str:
    query = """
        SELECT g.id, g.name
        FROM content.genre g 
        JOIN content.genre_film_work g_f_w ON g.id = g_f_w.genre_id
        WHERE g_f_w.film_work_id = '{id_}';
    """.format(
        id_=film_work_id,
    )
    return query
