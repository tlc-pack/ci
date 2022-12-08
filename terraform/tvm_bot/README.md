# tvm-bot

This folder holds the code for tvm-bot, a generic framework for responding to GitHub webhooks for Apache TVM. To file issues or request features, please [create an issue in apache/tvm](https://github.com/apache/tvm/issues/new?assignees=&labels=needs-triage%2C+type%3Aci&title=) with `[tvm-bot]` in the title.

## Components

### Welcome Message

When a PR is created, tvm-bot posts a generic message with links to the contributing docs. This same comment is used by other components to add information as it becomes available.

### Topic-based Tagging

[apache/tvm#10317](https://github.com/apache/tvm/issues/10317) allows developers to specify a mapping of topics to GitHub usernames. When these topics are mentioned in a PR title or labels, the relevant GitHub usernames are tagged in the tvm-bot comment.

### Skipped Tests

It can be tricky to determine what changed between a PR's test report and what happened in the base commit on main. This component leaves a comment with the diff of tests ran/skipped on a PR's most recent CI run and the CI run of the commit on which the PR's `HEAD` was created.

### Rendered Docs

Part of TVM's CI builds the TVM documentation and uploads it to S3. This component leaves a PR-specific link to the docs for the most recent successful CI run.

### CI Runtime

PRs that significantly change CI runtime should bear extra scrutiny to ensure the change was intentional. This component leaves a comment with the percent change of CI runtime of the most recent build versus the mean of the last several successful post-merge CI runs on `main`.

## Development

tvm-bot runs on AWS Lambda via a webhook configured in the apache/tvm repo. It is deployed via the [`tvm_bot.tf`](../tvm_bot.tf) Terraform script which packages up the Python code and creates a Lambda function with the necessary API gateway and IAM plumbing.

To add a handler, create a function in [`handlers.py`](./handlers.py) and register it with the relevant webhook events in [`lambda_function.py`](./lambda_function.py). Add a test in [`test/`](./test/) and run the suite with:

```bash
make tests
```

