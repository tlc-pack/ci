import os

from py_github_webhook import PyGitHubWebhook, Trigger, main, init_logger
from handlers import open_or_edit_pr, pr_status


# Create and register the handlers for each webhook event
handlers = {
    Trigger.PULL_REQUEST: open_or_edit_pr,
    Trigger.STATUS: pr_status,
}
init_logger("py-github")
HANDLER = PyGitHubWebhook(handlers=handlers, secret=os.environ["WEBHOOK_SECRET"])


def lambda_handler(event, context):
    """
    AWS Lambda executes this function whenever the function is invoked
    """
    response = HANDLER.lambda_handler(event, context)
    return response


if __name__ == "__main__":
    # This is used solely for local runs and debugging
    os.environ["SKIP_COMMENT"] = "1"
    response = main(handler=HANDLER)
    print(response)
