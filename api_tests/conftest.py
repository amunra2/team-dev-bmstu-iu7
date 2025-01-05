from pathlib import Path
from shutil import copy

from backend.app import create_app

import pytest


PROJECT_ROOT = Path(__file__).parent.parent
TEST_DB = "test.db"


@pytest.fixture
def client(tmpdir):
    copy(f"{PROJECT_ROOT}/{TEST_DB}", tmpdir.dirpath())
    db_connection = f"sqlite:///{tmpdir.dirpath()}/{TEST_DB}"

    app = create_app(db_connection)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
