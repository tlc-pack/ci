import argparse
import asyncio
import re
import statistics
import math
import rich

from typing import *

from utils import forward
from utils.forward import *


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


def analyze_stages(stage_name: str, stages: List[Stage], goal_runtime_m: float):
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

    print(f"       fixed runtime (m): {round(fixed_runtime_m, 2)}")
    print(f"    parallel runtime (m): {round(parallelizable_runtime_m, 2)}")
    print(f"         required shards: {num_shards}")


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


def analyze(build: Build, goal_runtime_m: float):
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
        analyze_stages(name, stages, goal_runtime_m)


async def main(args):
    async with aiohttp.ClientSession() as s:
        forward.SESSION = s
        data = await fetch_branch(name=args.branch)
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Determine number of Jenkins shards to use"
    )
    parser.add_argument("--runtime-goal-m", required=True)
    parser.add_argument("--list-steps", action="store_true")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--build", default="4082")
    args = parser.parse_args()
    init(dir=".httpcache")
    init_log()

    branch = asyncio.run(main(args))
    build = branch.builds[0]

    if args.list_steps:
        list_steps(build)
    else:
        print(f"To reach goal runtime of {args.runtime_goal_m} for tests:")
        analyze(build, goal_runtime_m=float(args.runtime_goal_m))
