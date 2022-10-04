#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os
import json
import argparse
import logging
import re
from typing import Dict, Any, List, Tuple, Optional


from .git_utils import git, GitHubRepo, parse_remote, find_ccs, dry_run_token
from .cmd_utils import tags_from_title


GITHUB_NAME_REGEX = r"@[a-zA-Z0-9-]+"


def parse_line(line: str) -> Tuple[str, List[str]]:
    line = line.lstrip(" -")
    line = line.split()

    # Parse out the name as anything up until the first tagged person
    tag_items = []
    tag_end = 0
    for i, piece in enumerate(line):
        if piece.startswith("@"):
            tag_end = i
            break

        tag_items.append(piece)

    tag = " ".join(tag_items).rstrip(":")

    # From the last word that was part of the tag name, start looking for users
    # tagged with a '@'
    users = []
    for piece in line[tag_end:]:
        if piece.startswith("@"):
            users.append(piece.lstrip("@"))

    return (tag, list(sorted(users)))


def fetch_issue(github: GitHubRepo, issue_number: int):
    query = """query($owner: String!, $name: String!, $number: Int!){
    repository(owner: $owner, name: $name) {
        issue(number: $number) {
        body
        comments(first:100) {
            nodes {
            body
            }
        }
        }
    }
    }"""
    r = github.graphql(
        query,
        variables={
            "owner": github.user,
            "name": github.repo,
            "number": issue_number,
        },
    )
    return r


def parse_teams(r: Dict[str, Any], issue_number: int) -> Dict[str, str]:
    """
    Fetch an issue and parse out series of tagged people from the issue body
    and comments
    """
    issue = r["data"]["repository"]["issue"]

    if issue is None or issue.get("body") is None:
        raise RuntimeError(
            f"Could not find issue #{issue_number}\n\n{json.dumps(r, indent=2)}"
        )

    result = {}

    def add_tag(tag, users):
        if tag in result:
            result[tag] += users
        else:
            result[tag] = users

    # Parse the issue body (only bullets are looked at)
    for line in issue["body"].split("\n"):
        line = line.strip()
        if not line.startswith("- "):
            continue
        if "@" not in line:
            continue

        tag, users = parse_line(line)
        add_tag(tag, users)

    # Parse comment bodies
    for comment in issue["comments"]["nodes"]:
        for line in comment["body"].split("\n"):
            if "@" not in line:
                continue

            tag, users = parse_line(line)
            add_tag(tag, users)

    # De-duplicate users listed twice for the same tag
    for tag in result:
        result[tag] = list(set(result[tag]))

    return {k.lower(): v for k, v in result.items() if k.strip()}


def tags_from_labels(labels: List[Dict[str, Any]]) -> List[str]:
    return [label["name"] for label in labels]


def add_ccs_to_body(body: str, to_cc: List[str]) -> str:
    lines = body.split("\n")

    cc_line_idx = None
    for i, line in enumerate(reversed(lines)):
        if line.strip() == "":
            continue
        if line.startswith("cc @"):
            cc_line_idx = len(lines) - i - 1
        else:
            break

    def gen_cc_line(users):
        users = sorted(users)
        return "cc " + " ".join([f"@{user}" for user in users])

    if cc_line_idx is None:
        print("Did not find existing cc line")
        lines.append("")
        lines.append(gen_cc_line(to_cc))
    else:
        # Edit cc line in place
        line = lines[cc_line_idx]
        print(f"Found existing cc line at {cc_line_idx}: {line}")
        existing_ccs = find_ccs(line)
        print(f"Found cc's: {existing_ccs}")

        if set(to_cc).issubset(set(existing_ccs)):
            # Don't do anything if there is no update needed
            return None

        line = gen_cc_line(set(existing_ccs + to_cc))

        lines[cc_line_idx] = line

    return "\n".join(lines)


def determine_users_to_cc(
    issue: Dict[str, Any],
    github: GitHubRepo,
    team_issue: str,
    issue_data: Optional[Dict[str, Any]],
) -> List[str]:
    logger = logging.getLogger("py-github")
    if issue_data is None:
        logger.info("No issue data passed in, fetching from GitHub")

    issue_data = fetch_issue(github, issue_number=int(team_issue))

    # Fetch the list of teams
    teams = parse_teams(issue_data, issue_number=int(team_issue))

    logger.info(
        f"Found these teams in issue #{team_issue}\n{json.dumps(teams, indent=2)}"
    )

    title = issue["title"]
    if "author" in issue:
        author = issue["author"]["login"]
    else:
        author = issue["user"]["login"]
    tags = tags_from_title(title)
    if isinstance(issue["labels"], dict):
        tags += tags_from_labels(issue["labels"]["nodes"])
    else:
        tags += tags_from_labels(issue["labels"])

    tags = [t.lower() for t in tags]
    logger.info(f"Found tags in title: {tags}")

    # Update the PR or issue based on tags in the title and GitHub tags
    to_cc = [teams.get(t, []) for t in tags]
    to_cc = list(set(item for sublist in to_cc for item in sublist))
    to_cc = [user for user in to_cc if user != author]
    return tags, sorted(to_cc)


def get_tags(
    pr_data: Dict[str, Any], github: GitHubRepo, team_issue: int
) -> Tuple[bool, str]:
    logger = logging.getLogger("py-github")
    tags, to_cc = determine_users_to_cc(
        issue=pr_data, github=github, team_issue=team_issue, issue_data=None
    )

    if pr_data["isDraft"]:
        logger.info("Ignoring draft PR")
        return False, None

    logger.info(f"Users to cc based on labels: {to_cc}")
    description = " <sub>See [#10317](https://github.com/apache/tvm/issues/10317) for details</sub>"
    if len(to_cc) == 0:
        if len(tags) == 0:
            return (
                False,
                "No users to auto-tag found, no teams are specified in PR title"
                + description,
            )
        else:
            tags_list = ", ".join([f"`{t}`" for t in tags])
            return False, f"No users to tag found in teams: {tags_list}" + description

    return False, "cc " + ", ".join([f"@{user}" for user in to_cc]) + description
