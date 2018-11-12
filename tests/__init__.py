
import pytest

from hospudka.app import create_app


@pytest.fixture(scope='module', autouse=True)
def app():
    yield create_app()
