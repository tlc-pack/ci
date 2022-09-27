import hashlib
import hmac
import json

from typing import Dict, Any

import lambda_function


def sign_payload(payload: Dict[str, Any], webhook_secret: str) -> str:
    payload_data = json.dumps(payload).encode("utf-8")
    signature = hmac.new(
        webhook_secret.encode("utf-8"), payload_data, hashlib.sha256
    ).hexdigest()
    return signature


def invoke_lambda(
    event_type: str, data: Dict[str, Any], webhook_secret: str = "test"
) -> Any:
    event = {
        "body": json.dumps(data),
        "headers": {
            "X-Hub-Signature-256": f"payload={sign_payload(payload=data, webhook_secret=webhook_secret)}",
            "X-GitHub-Event": event_type,
        },
    }
    return lambda_function.lambda_handler(event=event, context=None)


def test_invalid_secret() -> None:
    """
    Ensure that requests without the proper signature will get 403 errors
    """
    result = invoke_lambda("status", {}, webhook_secret="bad")
    assert result["statusCode"] == 403
    assert result["body"] == "Forbidden"


def test_invalid_event() -> None:
    """
    Ensure that irrelevant events are ignored
    """
    result = invoke_lambda("something", {})
    assert result["statusCode"] == 400
    assert result["body"] == "Not processing event"
