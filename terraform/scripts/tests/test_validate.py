from validate import validate


def test_validate():
    # Assert that MR from local repo passes validation
    assert (
        validate("test_repo", "test_repo", "pull_request", "test_email", [], True)
        == True
    )
    # Assert that unverified commit fails validation
    assert (
        validate("test_repo", "test_repo", "pull_request", "test_email", [], False)
        == False
    )
    # Assert that if PR and target repos are different, validation fails
    assert (
        validate(
            "test_repo", "different_test_repo", "pull_request", "test_email", [], True
        )
        == False
    )
    # Assert that if verified commit from fork and committer email in DEPLOYERS.md, validation passes
    assert (
        validate(
            "test_repo",
            "different_test_repo",
            "pull_request_target",
            "test_email",
            ["test_email"],
            True,
        )
        == True
    )
    # Assert that unverified commit fails validation
    assert (
        validate(
            "test_repo",
            "different_test_repo",
            "pull_request_target",
            "test_email",
            ["test_email"],
            False,
        )
        == False
    )
