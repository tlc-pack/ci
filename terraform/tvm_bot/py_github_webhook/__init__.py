import argparse
import hashlib
import hmac
import json
import os

from typing import Dict, Any, Optional, Callable, Union, List, Mapping
from .log import init_logger


class Trigger:
    # See https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_EDITED = "pull_request:edited"
    STATUS = "status"


Handler = Callable[[Dict[str, Any]], None]


def sign_payload(payload: Dict[str, Any], webhook_secret: str) -> str:
    payload_data = json.dumps(payload).encode("utf-8")
    signature = hmac.new(
        webhook_secret.encode("utf-8"), payload_data, hashlib.sha256
    ).hexdigest()
    return signature


def add_inplace(the_list, item):
    if isinstance(item, list):
        the_list.extend(item)
    else:
        the_list.append(item)


class PyGitHubWebhook:
    def __init__(
        self,
        handlers: Mapping[str, Union[Handler, List[Handler]]],
        secret: Optional[str] = None,
    ):
        self.secret = secret
        self.handlers = handlers
        self.log = init_logger("py-github")
        if self.secret is None:
            self.log.warn("secret was not provided to PyGitHubWebhook")

    def check_hash(self, payload: bytes, expected: str) -> bool:
        """
        GitHub webhooks should be signed with a predetermined secret. This returns
        True if the signature is valid.
        """
        signature = hmac.new(
            os.environ["WEBHOOK_SECRET"].encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    def lambda_handler(self, event, context) -> Dict[str, Any]:
        expected = event["headers"].get("X-Hub-Signature-256", "").split("=")[1]
        payload = event["body"].encode("utf-8")

        # Check that the signature matches the secret on GitHub
        if not self.check_hash(payload, expected):
            self.log.warn(f"Invalid signature provided in {event}")
            return {"statusCode": 403, "body": "Forbidden"}

        # Find the handlers for the event (e.g. pull_request)
        event_type = event["headers"]["X-GitHub-Event"]
        key = event_type

        handlers_to_run: List[Handler] = []
        add_inplace(the_list=handlers_to_run, item=self.handlers.get(event_type, []))

        # Find the handlers for specific event-action pairs
        # (e.g. pull_request:edited)
        data = json.loads(event["body"])
        action_type = data.get("action", None)
        if action_type is not None:
            key = f"{event_type}:{action_type}"
            add_inplace(the_list=handlers_to_run, item=self.handlers.get(key, []))

        self.log.info(f"Found {len(handlers_to_run)} handlers for {key}")

        if len(handlers_to_run) == 0:
            return {"statusCode": 400, "body": f"no handlers found: {key}"}
        # Run the handlers and merge their statuses
        status = 200
        for handler in handlers_to_run:
            self.log.info(f"Running {handler}")
            try:
                handler(data)
            except Exception as e:
                status = 500
                self.log.exception(e)

        return {"statusCode": status, "body": f"ok: {key}"}


def main(
    handler: PyGitHubWebhook, parser: Optional[argparse.ArgumentParser] = None
) -> Dict[str, Any]:
    """
    Handler for local runs
    """

    if parser is None:
        parser = argparse.ArgumentParser(description="Run the lambda handler")
        parser.add_argument("--payload", help="webhook JSON payload", required=True)
        parser.add_argument(
            "--no-dry-run", action="store_true", help="skip writing comment"
        )
        parser.add_argument(
            "--event",
            help="webhook event type (e.g. pull_request, status)",
            required=True,
        )
    args = parser.parse_args()

    os.environ["DEBUG"] = "0" if args.no_dry_run else "1"
    os.environ["WEBHOOK_SECRET"] = "test"

    if args.payload.endswith(".json"):
        with open(args.payload) as f:
            payload = json.load(f)
    else:
        payload = json.loads(args.payload)

    event = {
        "headers": {
            "X-Hub-Signature-256": "="
            + sign_payload(
                payload=payload, webhook_secret=os.environ["WEBHOOK_SECRET"]
            ),
            "X-GitHub-Event": args.event,
        },
        "body": json.dumps(payload),
    }
    response = handler.lambda_handler(event, context=None)
    return response
