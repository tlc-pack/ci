import dataclasses
import aiohttp
import asyncio
import datetime
import sys
import os
import time
import json
import argparse
import subprocess
from pathlib import Path
from sqlalchemy import select
from utils import *
from net import *
from typing import *
from forward import *
from forward import Branch, blue, init, init_log
import forward
from urllib.parse import unquote

import db
import schema
import logging

DEBUG = os.getenv("DEBUG", "0") == "1"
SCHEMA_SCRIPT = Path(__file__).resolve().parent / "schema.py"


def lstrip(s: str, prefix: str) -> str:
    if s.startswith(prefix):
        s = s[len(prefix) :]
    return s


def classname_to_file(classname: str) -> str:
    classname = lstrip(classname, "cython.")
    classname = lstrip(classname, "ctypes.")
    return classname.replace(".", "/") + ".py"


@dataclasses.dataclass
class TestCase:
    build_id: int
    branch_name: str
    blue_url: str
    status: str
    state: str
    duration_ms: float
    stage: str
    node_id: str
    name: str
    parameterless_name: str
    file_name: str


def store_tests_in_db(cases: List[TestCase]):
    engine = db.get_engine(db.connection_string("tvm"))

    def db_dict(table, obj):
        names = [c.name for c in table.columns]
        r = {}
        for n in names:
            r[n] = getattr(obj, n)
        return r

    def write(conn, table, obj):
        db.upsert(conn, table, db_dict(table, obj))

    logging.info(f"[db] Writing {len(cases)} cases")
    with engine.connect() as conn:
        for case in cases:
            write(conn, schema.testcase, case)


async def fetch_and_store_branch_tests(name: str) -> Branch:
    logging.info(f"Fetching branch {name}")
    branch_data = await blue(f"{name}", use_cache=False)
    branch = Branch(
        name=name,
        full_name=branch_data["fullName"],
        url=f"https://ci.tlcpack.ai/job/tvm/job/{name}/",
        blue_url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/tvm/activity?branch={name}",
        builds=[],
    )

    logging.info("Querying existing builds")

    # Jenkins only fetches the last 100 by default
    builds = await blue(f"{name}/runs", use_cache=False)
    logging.info(f"Found {len(builds)} builds for branch {name}")
    builds = list(reversed(sorted(builds, key=lambda b: int(b["id"]))))

    for build_data in builds:
        if build_data["state"] != "FINISHED":
            # Only look at completed builds
            logging.info(f"Build {build_data['id']} is incomplete, skipping")
            continue

        if build_data["result"] == "SUCCESS":
            # Only look at completed builds
            logging.info(f"Build {build_data['id']} is successful, skipping")
            continue

        build_id = build_data["id"]
        test_report_url = (
            f"https://ci.tlcpack.ai/job/tvm/job/{name}/{build_id}/testReport/api/xml"
        )
        logging.info(f"Fetching test report from {test_report_url}")

        failed = await blue(
            f"{name}/runs/{build_id}/tests/?status=FAILED&start=0&limit=101",
            no_slash=True,
        )
        if "code" in failed and failed["code"] == 404:
            logging.info(f"Build {build_id} failed without a report, skipping")
            continue

        if len(failed) == 0:
            continue

        failed_cases = []
        for item in failed:
            parts = unquote(item["name"]).split(" / ")
            stage = parts[:-1]

            name_parts = parts[-1].split(" – ")
            test_name = name_parts[0]
            parameterless_name = test_name.split("[")[0]
            suite = name_parts[1]
            node_id = classname_to_file(suite) + "::" + test_name

            case = TestCase(
                build_id=build_id,
                branch_name=name,
                blue_url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/tvm/detail/{name}/{build_id}/pipeline/",
                state=item["state"].lower(),
                status=item["status"].lower(),
                duration_ms=int(item["duration"] * 1000),
                stage=" / ".join(stage),
                node_id=node_id,
                name=test_name,
                parameterless_name=parameterless_name,
                file_name=classname_to_file(suite),
            )
            failed_cases.append(case)

        logging.info(f"Found {len(failed_cases)} failed test cases")

        store_tests_in_db(failed_cases)

    return branch


async def main(args):
    global SESSION
    async with aiohttp.ClientSession() as s:
        SESSION = s
        forward.SESSION = s

        runs = await aioget(
            "https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/tvm/runs/",
            session=s,
            use_cache=False,
        )
        runs = json.loads(runs)
        branch_names = set(r["pipeline"] for r in runs)
        branch_names.add("main")
        branch_names = list(sorted(branch_names, key=lambda a: 0 if a == "main" else 1))
        # branch_names = ["main"]

        for name in branch_names:
            await fetch_and_store_branch_tests(name)
            time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Jenkins tests and store it in Postgres"
    )
    parser.add_argument("--forever", action="store_true", help="loop and re-fetch")
    parser.add_argument(
        "--wait-minutes", default=15, type=int, help="sleep time while looping"
    )
    args = parser.parse_args()
    init(dir=".httpcache")
    init_log()

    if args.forever:
        subprocess.run([sys.executable, str(SCHEMA_SCRIPT)], check=True)
        while True:
            asyncio.run(main(args))
            logging.info(f"Sleeping for {args.wait_minutes} minutes")
            time.sleep(args.wait_minutes * 60)
    else:
        asyncio.run(main(args))
