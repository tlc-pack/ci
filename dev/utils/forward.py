"""
Scrape Jenkins, send build data to Loki and Postgres
"""
import argparse
import asyncio
import dataclasses
import datetime
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import *

import aiohttp

from . import db, schema
from .net import *

# from sqlalchemy import select
from .utils import *

SESSION = None
DEBUG = os.getenv("DEBUG", "0") == "1"
SCHEMA_SCRIPT = Path(__file__).resolve().parent / "schema.py"
# LOKI_HOST = os.environ["loki_host"]


def walk(o, visitor):
    visitor(o)
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, visitor)
    elif isinstance(o, list):
        for v in o:
            walk(v, visitor)


async def blue(job_name: str, url: str, use_cache: bool = True, no_slash: bool = False) -> Any:
    if DEBUG:
        use_cache = True

    if not no_slash and not url.endswith("/"):
        url = url + "/"

    if SESSION is None:
        raise RuntimeError("SESSION is None")

    r = await aioget(
        f"https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/{job_name}/branches/{url}",
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
    job_name: str, branch_name: str, build: Build, stage_data: Dict[str, Any]
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
        url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/{job_name}/detail/{branch_name}/{build.id}/pipeline/{stage_data['id']}",
        steps=[],
    )

    steps_data = await blue(job_name, f"{branch_name}/runs/{build.id}/nodes/{stage.id}/steps")

    for step_data in steps_data:
        stage.steps.append(await fetch_step(job_name, branch_name, build, stage, step_data))

    return stage


async def fetch_step(
    job_name: str, branch_name: str, build: Build, stage: Stage, step_data: Dict[str, Any]
) -> Step:
    id = step_data["id"]
    log_url = f"https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/{job_name}/branches/{branch_name}/runs/{build.id}/nodes/{stage.id}/steps/{id}/log/"
    # log_url = f"https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/{job_name}/branches/{branch_name}/runs/{build.id}/steps/{id}/log/"
    # log = await aioget(log_url, session=SESSION)
    log = "dog"
    return Step(
        name=step_data["displayName"],
        id=step_data["id"],
        result=step_data["result"],
        started_at=parse_date(step_data["startTime"]),
        state=step_data["state"],
        description=step_data["displayDescription"],
        log_url=log_url,
        log=log,
        url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/{job_name}/detail/{branch_name}/{build.id}/pipeline/{stage.id}#step-{step_data['id']}",
        duration_ms=int(step_data["durationInMillis"]),
    )


async def fetch_build(job_name: str, branch_name: str, build_data: Dict[str, Any]) -> Build:
    queued_at = parse_date(build_data["enQueueTime"])
    started_at = parse_date(build_data["startTime"])
    ended_at = parse_date(build_data["endTime"])

    queue_time_ms = int((started_at - queued_at).total_seconds() * 1000)
    run_time_ms = int((ended_at - started_at).total_seconds() * 1000)
    causes = build_data["causes"]
    if causes is None:
        causes = []

    test_summary = await blue(job_name, f"{branch_name}/runs/{build_data['id']}/blueTestSummary")

    build = Build(
        causes=[c["shortDescription"] for c in causes],
        id=build_data["id"],
        url=f"https://ci.tlcpack.ai/job/{job_name}/job/{branch_name}/{build_data['id']}/",
        blue_url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/{job_name}/detail/{branch_name}/{build_data['id']}/pipeline",
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

    nodes_data = await blue(job_name, f"{branch_name}/runs/{build.id}/nodes")
    for stage_data in nodes_data:
        build.stages.append(await fetch_stage(job_name, branch_name, build, stage_data))

    return build


async def fetch_branch(job_name: str, name: str):
    logging.info(f"Fetching branch {name}")
    branch_data = await blue(job_name, f"{name}", use_cache=False)
    branch = Branch(
        name=name,
        full_name=branch_data["fullName"],
        url=f"https://ci.tlcpack.ai/job/{job_name}/job/{name}/",
        blue_url=f"https://ci.tlcpack.ai/blue/organizations/jenkins/{job_name}/activity?branch={name}",
        builds=[],
    )

    # Jenkins only fetches the last 100 by default
    builds = await blue(job_name, f"{name}/runs", use_cache=False)
    logging.info(f"Found {len(builds)} builds for branch {name}")
    builds = list(reversed(sorted(builds, key=lambda b: int(b["id"]))))
    for build_data in builds:
        if build_data["state"] != "FINISHED":
            # Only look at completed builds
            continue

        branch.builds.append(await fetch_build(job_name, name, build_data))
        break

    return branch

