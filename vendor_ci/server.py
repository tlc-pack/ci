import json
import os
import re

from flask import Flask, request, g, jsonify
import boto3
import requests

app = Flask(__name__)

_test_api_keys = {
    "test": "tvm_abc123",
}
S3 = boto3.client("s3")
S3_BUCKET = os.getenv("S3_BUCKET", "tvm-vendor-ci-prod")
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OWNER = os.environ["GITHUB_OWNER"]
REPO = os.environ["GITHUB_REPO"]
API_KEYS = json.loads(os.getenv("API_KEYS_JSON", json.dumps(_test_api_keys)))

TOKEN_REGEX = re.compile(r"([a-zA-Z-]+):(tvm_[a-z0-9A-Z]+)")
SHA_REGEX = re.compile(r"[0-9a-f]{40}")
VALID_STATUSES = {"pending", "error", "success"}


def upload_log(file, name: str) -> None:
    S3.upload_fileobj(file, S3_BUCKET, name)


def add_commit_status(sha: str, name: str, description: str, status: str) -> None:
    """
    Update or add a commit status via the GitHub API for the commit 'sha'
    """
    print("Sending to github")
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    payload = {
        "state": status,
        "target_url": f"https://vendor-ci.tlcpack.ai/{name}",
        "description": description,
        "context": name,
    }

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/statuses/{sha}"
    print(f"POST to {url} with {payload}")
    r = requests.post(url, json=payload, headers=headers)
    print(r)


@app.before_request
def check_api_key():
    auth = request.headers.get("Authorization")
    if auth is None:
        return "Forbidden: missing 'Authorization' HTTP header", 403

    match = TOKEN_REGEX.match(auth)
    if not match:
        return (
            "Forbidden: malformed API key must be in the format: '<ci status name>:<the token>', for example 'my-status:tvm_abc1234'",
            403,
        )

    name, key = match.groups()
    print(name, key)
    if name not in API_KEYS:
        return "Forbidden: Unknown status name", 403

    if API_KEYS[name] != key:
        return "Forbidden: Invalid API key", 403

    g.api_name = name
    g.api_key = key


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("log")
    data = json.loads(request.form.get("data"))

    # Check the git SHA
    sha = data.get("sha")
    if sha is None:
        return jsonify({"error": f"no sha provided"}), 400
    if not isinstance(sha, str):
        return jsonify({"error": f"malformed git sha: {sha}, not a string"}), 400
    if len(sha) != 40:
        return (
            jsonify({"error": f"malformed git sha: {sha}, must be 40 characters"}),
            400,
        )
    if SHA_REGEX.match(sha) is None:
        return (
            jsonify({"error": f"malformed git sha: {sha}, has invalid characters"}),
            400,
        )

    # Check the status
    status = data.get("status")
    if status is None:
        return jsonify({"error": f"no status provided"}), 400
    if status not in VALID_STATUSES:
        return (
            jsonify(
                {"error": f"status must be one of: {VALID_STATUSES}, got {status}"}
            ),
            400,
        )

    # Check the description
    description = data.get("description")
    if description is None:
        return jsonify({"error": f"no description provided"}), 400
    if not isinstance(description, str):
        return (
            jsonify({"error": f"malformed description: {description}, not a string"}),
            400,
        )
    if len(description) > 40:
        return (
            jsonify({"error": f"malformed description: {description}, too long"}),
            400,
        )

    if status != "pending":
        name = f"{g.api_key}/{sha}"
        if file is None:
            return (
                jsonify(
                    {
                        "error": f"log file not provided but status was not pending: {status}"
                    }
                ),
                400,
            )
        upload_log(file=file, name=name)

    add_commit_status(sha=sha, name=g.api_name, description=description, status=status)

    return jsonify(
        {"body": f"updated status to {status} for {g.api_name} on commit {sha}"}
    )
