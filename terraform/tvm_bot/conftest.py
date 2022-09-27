import os


def pytest_generate_tests(metafunc):
    # lambda_function needs a WEBHOOK_SECRET to run, so set that up for local
    # testing
    os.environ["WEBHOOK_SECRET"] = "test"
