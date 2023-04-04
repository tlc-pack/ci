import os
import sys

from github import Github


def sprint(*args):
    print(*args, file=sys.stderr)


def check_is_verified(token, repository, ref):
    client = Github(login_or_token=token)
    repo = client.get_repo(repository)
    latest_commit = repo.get_commit(ref)
    return latest_commit.commit.raw_data["verification"]["verified"]


def validate(
    github_repository,
    working_repository,
    github_event_name,
    committer_login,
    deployers,
    is_verified,
):
    is_fork = not github_repository == working_repository
    is_deployer = committer_login in deployers
    is_pull_request_event = github_event_name == "pull_request"
    is_pull_request_target_event = github_event_name == "pull_request_target"

    is_fork_and_is_ok = is_fork and is_deployer and is_pull_request_target_event
    not_fork_and_is_ok = not is_fork and is_pull_request_event
    sprint("Validating workflow with:")
    sprint(f"    is_verified:                  {is_verified}")
    sprint(f"    is_fork:                      {is_fork}")
    sprint(f"    is_deployer:                  {is_deployer}")
    sprint(f"    is_pull_request_event:        {is_pull_request_event}")
    sprint(f"    is_pull_request_target_event: {is_pull_request_target_event}")
    sprint(f"    is_fork_and_is_ok:            {is_fork_and_is_ok}")
    sprint(f"    not_fork_and_is_ok:           {not_fork_and_is_ok}")

    valid_workflow = is_verified and (is_fork_and_is_ok or not_fork_and_is_ok)
    return valid_workflow


if __name__ == "__main__":
    deployer_path = os.environ["GITHUB_WORKSPACE"] + "/terraform/DEPLOYERS.md"
    with open(deployer_path) as file:
        deployers = [i.strip() for i in file]

    token = os.environ["GITHUB_TOKEN"]
    github_repository = os.environ["GITHUB_REPOSITORY"]
    working_repository = os.environ["PR_REPO_FULL_NAME"]
    pr_branch_name = os.environ["GITHUB_HEAD_REF"]
    github_event_name = os.environ["GITHUB_EVENT_NAME"]
    committer_login = os.environ["LOGIN"]

    is_verified = check_is_verified(token, working_repository, pr_branch_name)
    valid_workflow = validate(
        github_repository,
        working_repository,
        github_event_name,
        committer_login,
        deployers,
        is_verified,
    )

    print(valid_workflow)
