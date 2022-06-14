"""
Scrape Jenkins, send build data to Loki and Postgres
"""
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

import db
import schema
import logging

SESSION = None
DEBUG = os.getenv("DEBUG", "0") == "1"
SCHEMA_SCRIPT = Path(__file__).resolve().parent / "schema.py"
LOKI_HOST = os.environ["loki_host"]


def walk(o, visitor):
    visitor(o)
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, visitor)
    elif isinstance(o, list):
        for v in o:
            walk(v, visitor)


async def blue(url: str, use_cache: bool = True, no_slash: bool = False) -> Any:
    if DEBUG:
        use_cache = True

    if not no_slash and not url.endswith("/"):
        url = url + "/"

    if SESSION is None:
        raise RuntimeError("SESSION is None")

    r = await aioget(
        f"https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/tvm/branches/{url}",
        session=SESSION,
        use_cache=use_cache,
    )
    r = json.loads(r)
    # These just clog up stuff for debugging
    def cleaner(o):
        if isinstance(o, dict):
            if "_links" in o:
                del o["_links"]
            if "_class" in o:
                del o["_class"]

    walk(r, cleaner)
    return r


@dataclasses.dataclass
class Step:
    name: str
    id: int
    result: str
    started_at: datetime.datetime
    state: str
    description: str
    log_url: str
    duration_ms: int
    url: str
    log: str


@dataclasses.dataclass
class Stage:
    name: str
    id: int
    duration_ms: int
    state: str
    result: str
    started_at: datetime.datetime
    parent: Optional["Stage"]
    url: str
    steps: List[Step]


@dataclasses.dataclass
class Build:
    causes: List[str]
    id: int
    url: str
    state: str
    result: str
    run_time_ms: int
    queue_time_ms: int
    queued_at: datetime.datetime
    started_at: datetime.datetime
    ended_at: datetime.datetime
    duration_ms: int
    commit: str
    blue_url: str
    failed_tests: int
    fixed_tests: int
    passed_tests: int
    regressed_tests: int
    skipped_tests: int
    total_tests: int
    stages: List[Stage]


@dataclasses.dataclass
class Branch:
    name: str
    full_name: str
    url: str
    blue_url: str
    builds: List[Build]


# A branch has a number of builds which have nodes that are made of steps
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


def parse_date(d: str) -> datetime.datetime:
    return datetime.datetime.strptime(d, DATE_FORMAT)


async def fetch_stage(
    branch_name: str, build: Build, stage_data: Dict[str, Any]
) -> Stage:
    stage = Stage(
        name=stage_data["displayName"],
        started_at=None
        if stage_data["startTime"] is None
        else parse_date(stage_data["startTime"]),
        duration_ms=int(stage_data["durationInMillis"]),
        state=stage_data["state"],
        result=stage_data["result"],
        id=stage_data["id"],
        parent=stage_data["firstParent"],
        url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/tvm/detail/{branch_name}/{build.id}/pipeline/{stage_data['id']}",
        steps=[],
    )

    steps_data = await blue(f"{branch_name}/runs/{build.id}/nodes/{stage.id}/steps")

    for step_data in steps_data:
        stage.steps.append(await fetch_step(branch_name, build, stage, step_data))

    return stage


async def fetch_step(
    branch_name: str, build: Build, stage: Stage, step_data: Dict[str, Any]
) -> Step:
    id = step_data["id"]
    log_url = f"https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/tvm/branches/{branch_name}/runs/{build.id}/nodes/{stage.id}/steps/{id}/log/"
    # log_url = f"https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/tvm/branches/{branch_name}/runs/{build.id}/steps/{id}/log/"
    log = await aioget(log_url, session=SESSION)
    return Step(
        name=step_data["displayName"],
        id=step_data["id"],
        result=step_data["result"],
        started_at=parse_date(step_data["startTime"]),
        state=step_data["state"],
        description=step_data["displayDescription"],
        log_url=log_url,
        log=log,
        url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/tvm/detail/{branch_name}/{build.id}/pipeline/{stage.id}#step-{step_data['id']}",
        duration_ms=int(step_data["durationInMillis"]),
    )


async def fetch_build(branch_name: str, build_data: Dict[str, Any]) -> Build:
    queued_at = parse_date(build_data["enQueueTime"])
    started_at = parse_date(build_data["startTime"])
    ended_at = parse_date(build_data["endTime"])

    queue_time_ms = int((started_at - queued_at).total_seconds() * 1000)
    run_time_ms = int((ended_at - started_at).total_seconds() * 1000)
    causes = build_data["causes"]
    if causes is None:
        causes = []

    test_summary = await blue(f"{branch_name}/runs/{build_data['id']}/blueTestSummary")

    build = Build(
        causes=[c["shortDescription"] for c in causes],
        id=build_data["id"],
        url=f"https://ci.tlcpack.ai/job/tvm/job/{branch_name}/{build_data['id']}/",
        blue_url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/tvm/detail/{branch_name}/{build_data['id']}/pipeline",
        state=build_data["state"],
        result=build_data["result"],
        queued_at=queued_at,
        started_at=started_at,
        ended_at=ended_at,
        run_time_ms=run_time_ms,
        queue_time_ms=queue_time_ms,
        duration_ms=int(build_data["durationInMillis"]),
        commit=build_data["commitId"],
        stages=[],
        failed_tests=test_summary["failed"],
        fixed_tests=test_summary["fixed"],
        passed_tests=test_summary["passed"],
        regressed_tests=test_summary["regressions"],
        skipped_tests=test_summary["skipped"],
        total_tests=test_summary["total"],
    )

    nodes_data = await blue(f"{branch_name}/runs/{build.id}/nodes")
    for stage_data in nodes_data:
        build.stages.append(await fetch_stage(branch_name, build, stage_data))

    return build


async def fetch_branch(name):
    logging.info(f"Fetching branch {name}")
    branch_data = await blue(f"{name}", use_cache=False)
    branch = Branch(
        name=name,
        full_name=branch_data["fullName"],
        url=f"https://ci.tlcpack.ai/job/tvm/job/{name}/",
        blue_url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/tvm/activity?branch={name}",
        builds=[],
    )

    # Jenkins only fetches the last 100 by default
    builds = await blue(f"{name}/runs", use_cache=False)
    logging.info(f"Found {len(builds)} builds for branch {name}")
    builds = list(reversed(sorted(builds, key=lambda b: int(b["id"]))))
    for build_data in builds:
        if build_data["state"] != "FINISHED":
            # Only look at completed builds
            continue

        branch.builds.append(await fetch_build(name, build_data))

    return branch


def upload_log(branch: Branch, build: Build, stage: Stage, step: Step) -> None:
    LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    lines = step.log.split("\n")
    lines = [[str(time.time_ns()), line[27:]] for line in lines if line.strip() != ""]

    url = f"http://{LOKI_HOST}/loki/api/v1/push"
    headers = {"Content-type": "application/json"}
    labels = {
        "branch_name": branch.name,
        "branch_full_name": branch.full_name,
        "branch_url": branch.url,
        "branch_blue_url": branch.blue_url,
        "build_id": build.id,
        "build_url": build.url,
        "build_state": build.state,
        "build_commit": build.commit,
        "stage_name": stage.name,
        "stage_id": stage.id,
        "stage_state": stage.state,
        "stage_result": stage.result,
        "step_name": step.name,
        "step_id": step.id,
        "step_result": step.result,
        "step_state": step.state,
        "step_description": step.description,
        "step_log_url": step.log_url,
    }

    payload = {"streams": [{"stream": labels, "values": lines}]}
    payload = json.dumps(payload)
    logging.info(f"Uploading logs for {stage.name} / {step.name} at {step.url}")
    r = requests.post(url, data=payload, headers=headers)
    logging.info(f"Loki responded {r}")
    if r.status_code >= 200 and r.status_code < 300:
        print("ok")
    else:
        r = json.loads(r.content.decode())
        jprint(r)
        raise RuntimeError(f"Failed to upload: {r['message']}")


def upload_sql(branch: Branch, build: Build) -> None:
    engine = db.get_engine(db.connection_string("tvm"))

    def db_dict(table, obj, stage=None):
        names = [c.name for c in table.columns]
        r = {}
        for n in names:
            if hasattr(obj, n):
                r[n] = getattr(obj, n)
            else:
                if n == "branch_name":
                    v = branch.name
                elif n == "build_id":
                    v = build.id
                elif n == "stage_id":
                    v = stage.id
                r[n] = v
        return r

    def write(conn, table, obj, stage=None):
        db.upsert(conn, table, db_dict(table, obj, stage))

    logging.info(
        f"[db] Writing {len(build.stages)} stages on build {build.id} for {branch.name} ({build.blue_url})"
    )
    with engine.connect() as conn:
        for stage in build.stages:
            for step in stage.steps:
                write(conn, schema.step, step, stage=stage)
            write(conn, schema.stage, stage)
        write(conn, schema.branch, branch)
        write(conn, schema.build, build)


async def fetch_and_store_branch(name: str) -> Branch:
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
    engine = db.get_engine(db.connection_string("tvm"))

    # Jenkins only fetches the last 100 by default
    builds = await blue(f"{name}/runs", use_cache=False)
    logging.info(f"Found {len(builds)} builds for branch {name}")
    builds = list(reversed(sorted(builds, key=lambda b: int(b["id"]))))
    # builds = [builds[10]]
    for build_data in builds:
        if build_data["state"] != "FINISHED":
            # Only look at completed builds
            logging.info(f"Build {build_data['id']} is incomplete, skipping")
            continue

        # If this build is in the DB already don't bother with it again
        build_id = int(build_data["id"])
        with engine.connect() as conn:
            s = (
                select(schema.build.c.branch_name, schema.build.c.id)
                .where(schema.build.c.id == build_id)
                .where(schema.build.c.branch_name == branch.name)
            )
            result = conn.execute(s)
            if result.rowcount != 0:
                logging.info(f"Found build {build_id} in DB, skipping")
                continue
            else:
                logging.info(f"Fetching build {build_id}")

        build = await fetch_build(name, build_data)
        logging.info(
            f"Uploading branch {branch.name} build {build.id} builds to DB and Loki"
        )
        for stage in build.stages:
            for step in stage.steps:
                upload_log(branch, build, stage, step)
        upload_sql(branch, build)
        branch.builds.append(await fetch_build(name, build_data))

    return branch


async def main(args):
    global SESSION
    async with aiohttp.ClientSession() as s:
        SESSION = s

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
            await fetch_and_store_branch(name)
            time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Jenkins data and store it in Postgres + Loki"
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
