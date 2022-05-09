import pytest
from validate import validate

test_data = {
    "valid-local-pull-request": {
        "github_repository": "test_repo",
        "working_repository": "test_repo",
        "github_event_name": "pull_request",
        "committer_email": "test_email",
        "deployers": "[]",
        "is_verified": True,
        "expected": True,
    },
    "unverified-local-pull-request": {
        "github_repository": "test_repo",
        "working_repository": "test_repo",
        "github_event_name": "pull_request",
        "committer_email": "test_email",
        "deployers": "[]",
        "is_verified": False,
        "expected": False,
    },
    "fork-pull-request": {
        "github_repository": "test_repo",
        "working_repository": "different_test_repo",
        "github_event_name": "pull_request",
        "committer_email": "test_email",
        "deployers": "[]",
        "is_verified": True,
        "expected": False,
    },
    "valid-fork-pull-request-target": {
        "github_repository": "test_repo",
        "working_repository": "different_test_repo",
        "github_event_name": "pull_request_target",
        "committer_email": "test_email",
        "deployers": ["test_email"],
        "is_verified": True,
        "expected": True,
    },
    "unverified-fork-pull-request-target": {
        "github_repository": "test_repo",
        "working_repository": "different_test_repo",
        "github_event_name": "pull_request_target",
        "committer_email": "test_email",
        "deployers": ["test_email"],
        "is_verified": False,
        "expected": False,
    },
}


@pytest.mark.parametrize(
    [
        "github_repository",
        "working_repository",
        "github_event_name",
        "committer_email",
        "deployers",
        "is_verified",
        "expected",
    ],
    [tuple(d.values()) for d in test_data.values()],
    ids=test_data.keys(),
)
def test_validate(
    github_repository,
    working_repository,
    github_event_name,
    committer_email,
    deployers,
    is_verified,
    expected,
):
    assert (
        validate(
            github_repository,
            working_repository,
            github_event_name,
            committer_email,
            deployers,
            is_verified,
        )
        == expected
    )
