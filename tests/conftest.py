import os


def pytest_configure(config):
    # Force the test suite onto the test Postgres DB, regardless of the
    # developer's local .env APP_ENV setting, so tests can never touch prod.
    os.environ["APP_ENV"] = "test"
