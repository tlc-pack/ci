import argparse
import asyncio
import math
import re
import statistics
from typing import *

import rich

from utils import forward
from utils.forward import *
from utils.net import init
from utils.schema import Build, Stage
from utils.utils import init_log


def is_parallelizable(name: str, desc: str) -> bool:
    descs = {
        "Run CPU integration tests",
        "Run Hexagon tests",
        "Run Python GPU integration tests",
        "Run Python GPU unit tests",
        "Run Python frontend tests",
        "Run Python unit tests",
        "Run VTA tests in FSIM",
        "Run VTA tests in TSIM",
        "Run i386 integration tests",
        "Run test_arm_compute_lib test",
        "Run TOPI tests",
        "Run microTVM tests",
    }
    if name in descs:
        return True
    return False


def find_existing_shards(stage_name: str, template: str):
    with open(template) as f:
        content = f.read()
    
    m = re.search(f'name="{stage_name}"(.*\n)+?.*num_shards=(\d+)', content, flags=re.MULTILINE)
    if m is None:
        print(f"Could not find {stage_name} in {template}, is that the right file?")
        exit(1)
    # print("match", m)
    start, end = m.span()
    # print(content[start:end])
    return int(m.groups()[1])


def analyze_stages(stage_name: str, stages: List[Stage], goal_runtime_m: float, jenkins_dir: str):
    steps_across_shards = {}
    for stage in stages:
        for step in stage.steps:
            if step.name not in steps_across_shards:
                steps_across_shards[step.name] = []
            steps_across_shards[step.name].append(step)

    fixed_runtime_m = 0
    parallelizable_runtime_m = 0
    for name, steps in steps_across_shards.items():
        parallelizable = is_parallelizable(name, "")
        median_runtime_m = (
            statistics.median([step.duration_ms for step in steps]) / 1000.0 / 60.0
        )
        total_runtime_m = sum([step.duration_ms for step in steps]) / 1000.0 / 60.0
        if parallelizable:
            parallelizable_runtime_m += total_runtime_m
        else:
            fixed_runtime_m += median_runtime_m

    parallel_part = goal_runtime_m - fixed_runtime_m
    print(stage_name)
    if parallel_part <= 0:
        print(
            f"    fixed runtime is too long ({round(fixed_runtime_m, 2)}), cannot reach goal time"
        )
        return

    num_shards = parallelizable_runtime_m / parallel_part
    num_shards = math.ceil(num_shards)

    existing_shards = find_existing_shards(stage_name, jenkins_dir)

    print(f"       fixed runtime (m): {round(fixed_runtime_m, 2)}")
    print(f"    parallel runtime (m): {round(parallelizable_runtime_m, 2)}")
    if existing_shards == num_shards:
        print(f"         required shards: {num_shards} (no action required)")
    else:
        print(f"         required shards: change from {existing_shards} to {num_shards} in {jenkins_dir}")


def list_steps(build: Build):
    def total_rt(stage: Stage):
        return sum(step.duration_ms for step in stage.steps)

    build.stages = sorted(build.stages, key=total_rt)
    print("For build at", build.blue_url)
    for stage in build.stages:
        if stage.name in {"Build", "Test", "Deploy"}:
            continue
        total = sum(step.duration_ms for step in stage.steps)
        if len(stage.steps) == 0:
            rich.print(f"{stage.name}: skipped")
            continue
        median = statistics.median([step.duration_ms for step in stage.steps])
        m75 = statistics.median(
            [step.duration_ms for step in stage.steps if step.duration_ms > median]
        )
        rich.print(f"{stage.name}: {round(total /1000.0/60.0)}m")
        for step in stage.steps:
            if step.duration_ms > m75:
                rich.print(
                    f"    [bold red]{step.name}[/bold red]: {round(step.duration_ms / 1000.0 / 60.0, 2)}"
                )
            elif step.duration_ms > median:
                rich.print(
                    f"    [magenta]{step.name}[/magenta]: {round(step.duration_ms / 1000.0 / 60.0, 2)}"
                )
            else:
                rich.print(
                    f"    {step.name}: {round(step.duration_ms / 1000.0 / 60.0, 2)}"
                )


def analyze(build: Build, goal_runtime_m: float, jenkins_template):
    test_stages: List[Stage] = []
    should_add = False
    for stage in build.stages:
        if stage.name == "Test":
            should_add = True
        elif stage.name == "Deploy":
            should_add = False
        elif should_add:
            test_stages.append(stage)

    names_to_stages = {}
    for stage in test_stages:
        names_to_stages[stage.name] = stage

    merged_shards = {}
    for stage in test_stages:
        m = re.match(r"(.*) \d+ of \d+", stage.name)
        if m:
            base_name = m.groups()[0]
            if base_name not in merged_shards:
                merged_shards[base_name] = []
            merged_shards[base_name].append(stage)
        else:
            merged_shards[stage.name] = [stage]

    for name, stages in merged_shards.items():
        analyze_stages(name, stages, goal_runtime_m, jenkins_template)


async def main(args):
    async with aiohttp.ClientSession() as s:
        forward.SESSION = s
        data = await fetch_branch(job_name=args.job, name=args.branch)
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Determine number of Jenkins shards to use"
    )
    parser.add_argument("--runtime-goal-m", required=True)
    parser.add_argument("--list-steps", action="store_true")
    parser.add_argument("--job")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--build", default="4082")
    parser.add_argument("--jenkins-template")
    args = parser.parse_args()
    init(dir=".httpcache")
    init_log()

    branch = asyncio.run(main(args))
    build = branch.builds[0]

    if args.list_steps:
        list_steps(build)
    else:
        print(f"To reach goal runtime of {args.runtime_goal_m} for tests:")
        analyze(build, goal_runtime_m=float(args.runtime_goal_m), jenkins_template=args.jenkins_template)
