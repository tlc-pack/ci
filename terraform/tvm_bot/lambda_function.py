import hashlib
import hmac
import json
import os

from typing import Dict, Any
from tvm_bot import github_pr_comment


def check_hash(payload: bytes, expected: str) -> bool:
    """
    GitHub webhooks should be signed with a predetermined secret. This returns
    True if the signature is valid.
    """
    signature = hmac.new(
        os.environ["WEBHOOK_SECRET"].encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


def should_handle_event(event_type: str) -> bool:
    return event_type in {"status", "pull_request"}


def handle_event(event_type: str, data: Dict[str, Any]) -> None:
    user = os.environ["USER"]
    repo = os.environ["REPO"]
    if event_type == "pull_request":
        github_pr_comment.github_pr_comment(data, user=user, repo=repo, dry_run=False)


def lambda_handler(event, context):
    expected = event["headers"].get("X-Hub-Signature-256", "").split("=")[1]
    payload = event["body"].encode("utf-8")

    # Check that the signature matches the secret on GitHub
    if not check_hash(payload, expected):
        return {"statusCode": 403, "body": "Forbidden"}

    # Check that the webhook event is one that matters
    event_type = event["headers"]["X-GitHub-Event"]
    if not should_handle_event(event_type):
        return {"statusCode": 400, "body": "Not processing event"}

    data = json.loads(event["body"])
    handle_event(event_type, data)
    return {"statusCode": 200, "body": f"ok: {event_type}"}


if __name__ == "__main__":
    # For local runs
    import argparse

    parser = argparse.ArgumentParser(description="Run the lambda handler")
    parser.add_argument("--payload", help="webhook JSON payload", required=True)
    parser.add_argument(
        "--event", help="webhook event type (e.g. pull_request, status)", required=True
    )
    args = parser.parse_args()

    handle_event(args.event, json.loads(args.payload))
