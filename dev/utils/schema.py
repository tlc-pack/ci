from typing import Any, Dict

import sqlalchemy
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    column,
    table,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.sqltypes import Float

from . import db

Base = declarative_base()


def gen_table(name: str, columns: Dict[str, Any], base: Any) -> Any:
    the_class = type(
        name,
        (base,),
        {
            "__tablename__": name,
            "__table_args__": {"extend_existing": True},
            **columns,
        },
    )
    name = the_class.__tablename__
    model_data = [name]
    for k in [k for k in the_class.__dict__.keys() if not k.startswith("_")]:
        model_data.append(column(k))
    model = table(*model_data)
    model._pks = [k for k, v in columns.items() if v.primary_key]
    return model, the_class


branch, Branch = gen_table(
    "branch",
    {
        "name": Column(String(300), primary_key=True),
        "full_name": Column(String(300)),
        "url": Column(String(300)),
        "blue_url": Column(String(300)),
    },
    Base,
)

build, Build = gen_table(
    "build",
    {
        "causes": Column(Text),
        "id": Column(Integer, primary_key=True),
        "url": Column(String(300)),
        "blue_url": Column(String(300)),
        "state": Column(String(300)),
        "result": Column(String(300)),
        "queued_at": Column(DateTime),
        "started_at": Column(DateTime),
        "ended_at": Column(DateTime),
        "duration_ms": Column(Integer),
        "run_time_ms": Column(Integer),
        "queue_time_ms": Column(Integer),
        "failed_tests": Column(Integer),
        "fixed_tests": Column(Integer),
        "passed_tests": Column(Integer),
        "regressed_tests": Column(Integer),
        "skipped_tests": Column(Integer),
        "total_tests": Column(Integer),
        "commit": Column(String(300)),
        "branch_name": Column(String(300), primary_key=True),
    },
    Base,
)

stage, Stage = gen_table(
    "stage",
    {
        "name": Column(String(300)),
        "id": Column(Integer, primary_key=True),
        "duration_ms": Column(Integer),
        "state": Column(String(300)),
        "result": Column(String(300)),
        "started_at": Column(DateTime),
        "parent": Column(Integer),
        "url": Column(String(300)),
        "branch_name": Column(String(300), primary_key=True),
        "build_id": Column(Integer, primary_key=True),
    },
    Base,
)


step, Step = gen_table(
    "step",
    {
        "name": Column(Text),
        "id": Column(Integer, primary_key=True),
        "result": Column(String(300)),
        "started_at": Column(DateTime),
        "state": Column(String(300)),
        "description": Column(Text),
        "log_url": Column(String(300)),
        "duration_ms": Column(Integer),
        "url": Column(String(300)),
        "branch_name": Column(String(300), primary_key=True),
        "build_id": Column(Integer, primary_key=True),
        "stage_id": Column(Integer, primary_key=True),
    },
    Base,
)


testcase, TestCase = gen_table(
    "testcase",
    {
        "build_id": Column(Integer, primary_key=True),
        "branch_name": Column(String(300), primary_key=True),
        "blue_url": Column(String(300)),
        "status": Column(String(300)),
        "state": Column(String(300)),
        "duration_ms": Column(Integer),
        "stage": Column(String(500)),
        "node_id": Column(String(500), primary_key=True),
        "name": Column(String(500)),
        "parameterless_name": Column(String(500)),
        "file_name": Column(String(500)),
    },
    Base,
)


def create(db_name):
    connection = db.connection_string(db=None)
    print(connection)
    raw = db.get_engine(connection)
    from sqlalchemy.orm import sessionmaker

    session = sessionmaker(bind=raw)()
    session.connection().connection.set_isolation_level(0)
    try:
        session.execute(f"CREATE DATABASE {db_name}")
    except sqlalchemy.exc.ProgrammingError as e:
        if "already exists" not in str(e):
            raise e
    session.connection().connection.set_isolation_level(1)
    db.clear_engine()

    Base.metadata.create_all(db.get_engine(db.connection_string(db_name)))
    print("Done")


if __name__ == "__main__":
    create("tvm")
