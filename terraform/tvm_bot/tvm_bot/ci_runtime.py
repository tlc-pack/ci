import json
import statistics
from typing import List, Dict, Any

# import scipy.stats
import re
import logging

from .git_utils import GitHubRepo


MAIN_INFO_URL = "https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/tvm/runs/?branch=main&start=0&limit=26"


def find_target_url(pr_head: Dict[str, Any]) -> str:
    for status in pr_head["statusCheckRollup"]["contexts"]["nodes"]:
        if status.get("context", "") == "tvm-ci/pr-head":
            return status["targetUrl"]

    raise RuntimeError(f"Unable to find tvm-ci/pr-head status in {pr_head}")


def fetch_past_build_times_s(github: GitHubRepo) -> List[float]:
    """
    Get a list of runtimes in seconds for past builds on main
    """
    logger = logging.getLogger("py-github")
    data = github.get(MAIN_INFO_URL, add_base=False)
    build_times_s = []
    logger.info(f"Fetched {len(data)} builds from main")
    for item in data:
        # Only look at completed builds
        if not can_use_build(item):
            logging.info("Skipping failed build")
            continue

        duration = item["durationInMillis"]
        build_times_s.append(duration / 1000.0)

    return build_times_s


def can_use_build(build: Dict[str, Any]) -> bool:
    """
    Returns True if the build can be used as a sample runtime
    """
    return build["state"] == "FINISHED" and build["result"] == "SUCCESS"


def fetch_build_time_s(branch: str, build: str, github: GitHubRepo) -> float:
    """
    Get the runtime in seconds of the branch/build combo specified
    """
    build = int(build)
    info_url = f"https://ci.tlcpack.ai/blue/rest/organizations/jenkins/pipelines/tvm/runs/?branch={branch}&start=0&limit=25"
    data = github.get(info_url, add_base=False)

    for item in data:
        if item["id"] == str(build):
            if can_use_build(item):
                return item["durationInMillis"] / 1000.0
            else:
                raise RuntimeError(
                    f"Found build for {branch} with {build} but cannot use it: {item}"
                )

    raise RuntimeError(f"Unable to find branch {branch} with {build} in {data}")


def ci_runtime_comment(pr: Dict[str, Any], github: GitHubRepo) -> str:
    author = pr["author"]["login"]
    if author not in {"driazati", "gigiblender", "areusch"}:
        logging.info(f"Comment author not in allowlist: {author}")
        return False, None
    logger = logging.getLogger("py-github")

    # Find the info to query Jenkins
    pr_head = pr["commits"]["nodes"][0]["commit"]
    target_url = find_target_url(pr_head)
    logger.info(f"Got target url {target_url}")
    m = re.search(r"/job/(PR-\d+)/(\d+)", target_url)
    branch, build = m.groups()

    # Fetch the build times for main
    logger.info(f"Calculating CI runtime for {branch} with {build}")
    main_build_times_s = fetch_past_build_times_s(github=github)
    if len(main_build_times_s) == 0:
        logger.info("Found no usable builds on main, quitting")
        return False, None

    # Do a t-test on the build time from the PR
    x = statistics.mean(main_build_times_s)
    logger.info(f"Sample mean from main: {x}")
    current_build_time_s = fetch_build_time_s(branch=branch, build=build, github=github)
    # res = scipy.stats.ttest_1samp(main_build_times_s, current_build_time_s)

    # Round of the change for presentation
    # logger.info(f"t-stats: {res}")
    change = -(x - current_build_time_s) / x * 100.0
    significant = change > 30.0
    change = round(change, 2)
    if change > 0:
        change = "+" + str(change)

    mean_build_time_main_min = round(x / 60.0, 2)
    pr_build_time_min = round(current_build_time_s / 60.0, 2)

    description = f"{change}% ({mean_build_time_main_min}m -> {pr_build_time_min}m)"

    build_url = f"https://ci.tlcpack.ai/blue/organizations/jenkins/tvm/detail/{branch}/{build}/pipeline"
    if significant:
        # if res.pvalue < 0.05:
        return (
            False,
            f"This PR significantly changed [CI runtime]({build_url}): {description}",
        )
    else:
        return False, (
            f"This PR had no significant effect on [CI runtime]({build_url}): {description}"
        )
