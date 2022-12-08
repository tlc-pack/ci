import json
import logging
import re

from typing import Dict, Any

from tvm_bot import github_pr_comment


def open_or_edit_pr(data: Dict[str, Any]) -> None:
    """
    When a user opens or edits a PR, comment the welcome message and cc anyone
    tagged in the PR title/comments
    """
    logger = logging.getLogger("py-github")
    number = data["number"]
    if number <= 13041:
        logger.info(f"Skipping old PR {number}")
        return
    logger.info(f"Running for new PR: {number}")

    user = data["repository"]["owner"]["login"]
    repo = data["repository"]["name"]
    github_pr_comment.github_pr_comment(
        data, user=user, repo=repo, dry_run=False, commenters=["ccs"]
    )


def pr_status(data: Dict[str, Any]) -> None:
    """
    When a PR gets a status event and it's a success, comment the docs URL and
    any newly skipped tests
    """
    logger = logging.getLogger("py-github")
    state = data["state"]

    # Docs and skipped-tests only matter for finished statuses
    if state != "success":
        logger.info(f"Skipping status with state {state}")
        return

    # No PR in details link, probably a build from a branch
    m = re.search(
        r"https://ci.tlcpack.ai/job/tvm/job/PR-(\d+)/\d+/display/redirect",
        data["target_url"],
    )
    if not m:
        logger.info(f"Unable to find PR in status URL: {data['target_url']}")
        return

    pr_number = int(m.groups()[0])
    user = data["repository"]["owner"]["login"]
    repo = data["repository"]["name"]

    # github_pr_comment expects a PR to be passed in, so mock one up here
    pr_data = {"number": pr_number}

    github_pr_comment.github_pr_comment(
        pr_data,
        user=user,
        repo=repo,
        dry_run=False,
        commenters=["docs", "skipped-tests", "runtime"],
    )
