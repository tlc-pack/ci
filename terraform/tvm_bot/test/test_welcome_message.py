import textwrap
import pytest
import unittest
import logging

from tvm_bot import github_pr_comment
from tvm_bot import git_utils
import tvm_bot

from utils import parameterize_named, assert_in, patch_github


# pylint: disable=line-too-long
@parameterize_named(
    author_gate=dict(
        pr_author="abc",
        comments=[],
        expected="Skipping comment for author abc",
    ),
    new_comment=dict(
        pr_author="driazati",
        comments=[],
        expected="No existing comment found",
    ),
    update_comment=dict(
        pr_author="driazati",
        comments=[
            {
                "author": {"login": "tvm-bot"},
                "databaseId": "comment456",
                "body": "<!---bot-comment--> abc",
            }
        ],
        expected="PATCH to https://api.github.com/repos/apache/tvm/issues/comments/comment456",
    ),
    new_body=dict(
        pr_author="driazati",
        comments=[],
        expected="Commenting "
        + textwrap.dedent(
            """
        <!---bot-comment-->

        Thanks for contributing to TVM! Please refer to the contributing guidelines https://tvm.apache.org/docs/contribute/ for useful information and tips. Please request code reviews from [Reviewers](https://github.com/apache/incubator-tvm/blob/master/CONTRIBUTORS.md#reviewers) by @-ing them in a comment.

        <!--bot-comment-ccs-start-->
         * the cc<!--bot-comment-ccs-end--><!--bot-comment-skipped-tests-start-->
         * the skipped tests<!--bot-comment-skipped-tests-end--><!--bot-comment-docs-start-->
         * the docs<!--bot-comment-docs-end-->
        """
        ).strip(),
    ),
    update_body=dict(
        pr_author="driazati",
        comments=[
            {
                "author": {"login": "tvm-bot"},
                "databaseId": "comment456",
                "body": textwrap.dedent(
                    """
        <!---bot-comment-->

        Thanks for contributing to TVM! Please refer to the contributing guidelines https://tvm.apache.org/docs/contribute/ for useful information and tips. Please request code reviews from [Reviewers](https://github.com/apache/incubator-tvm/blob/master/CONTRIBUTORS.md#reviewers) by @-ing them in a comment.

        <!--bot-comment-ccs-start-->
         * the cc<!--bot-comment-ccs-end--><!--bot-comment-something-tests-start-->
         * something else<!--bot-comment-something-tests-end--><!--bot-comment-docs-start-->
         * the docs<!--bot-comment-docs-end-->
        """
                ).strip(),
            }
        ],
        expected="Commenting "
        + textwrap.dedent(
            """
        <!---bot-comment-->

        Thanks for contributing to TVM! Please refer to the contributing guidelines https://tvm.apache.org/docs/contribute/ for useful information and tips. Please request code reviews from [Reviewers](https://github.com/apache/incubator-tvm/blob/master/CONTRIBUTORS.md#reviewers) by @-ing them in a comment.

        <!--bot-comment-ccs-start-->
         * the cc<!--bot-comment-ccs-end--><!--bot-comment-something-tests-start-->
         * something else<!--bot-comment-something-tests-end--><!--bot-comment-docs-start-->
         * the docs<!--bot-comment-docs-end--><!--bot-comment-skipped-tests-start-->
         * the skipped tests<!--bot-comment-skipped-tests-end-->
        """
        ).strip(),
    ),
)
# pylint: enable=line-too-long
def test_pr_comment(caplog, monkeypatch, pr_author, comments, expected):
    """
    Test the PR commenting bot
    """
    target_url = "https://ci.tlcpack.ai/job/tvm/job/PR-11594/3/display/redirect"
    commit = {
        "commit": {
            "oid": "sha1234",
            "statusCheckRollup": {
                "contexts": {
                    "nodes": [
                        {
                            "context": "tvm-ci/pr-head",
                            "targetUrl": target_url,
                        }
                    ]
                }
            },
        }
    }

    bot_comment_sections = {
        "ccs": "the cc",
        "docs": "the docs",
        "skipped-tests": "the skipped tests",
    }
    if "bot-comment-ccs-start" in expected:
        pytest.skip("Comment sections not yet implemented")

    data = {
        "[1] POST - https://api.github.com/graphql": {},
        "[2] POST - https://api.github.com/graphql": {
            "data": {
                "repository": {
                    "pullRequest": {
                        "number": 1234,
                        "comments": {
                            "nodes": comments,
                        },
                        "author": {
                            "login": pr_author,
                        },
                        "commits": {
                            "nodes": [commit],
                        },
                    }
                }
            }
        },
    }

    patch_github(monkeypatch=monkeypatch, test_data=data)

    with caplog.at_level(logging.INFO):
        github_pr_comment.github_pr_comment(
            webhook_pr_data={
                "number": 1234,
            },
            user="apache",
            repo="tvm",
            dry_run=True,
        )

    assert_in(expected, caplog.text)
