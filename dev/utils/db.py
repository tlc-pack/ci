import os

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert


def connection_string(db="tvm"):
    host = os.environ["db_host"]
    password = os.environ["db_password"]
    user = os.environ["db_user"]

    if db is None:
        return f"postgresql://{user}:{password}@{host}"
    else:
        return f"postgresql://{user}:{password}@{host}/{db}"


engine = None


def get_engine(connection_string: str):
    global engine
    if engine is None:
        engine = create_engine(connection_string, echo=bool(os.getenv("ECHO", False)))

    return engine


def clear_engine():
    global engine
    engine = None


def upsert(engine, model, insert_dict):
    """
    Insert or update to an engine backed by MySQL
    """
    inserted = insert(model).values(**insert_dict)
    # MySQL version:
    # upserted = inserted.on_duplicate_key_update(
    #     **{k: inserted.inserted[k] for k, v in insert_dict.items()}
    # )

    # Postgres version:
    upserted = inserted.on_conflict_do_update(
        index_elements=model._pks,
        # index_where=my_table.c.user_email.like("%@gmail.com"),
        set_=insert_dict,
    )
    res = engine.execute(upserted)
    return res.lastrowid
