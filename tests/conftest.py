"""
Pytest configuration and fixtures.
"""

import os

# Set test database environment variables BEFORE any imports
os.environ["DB_NAME"] = "test_asdana"
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["BOT_TOKEN"] = "test_token"
os.environ["BOT_DESCRIPTION"] = "Test bot"

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    Set up test environment variables.
    """
    yield
