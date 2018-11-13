
import json
import pytest

from . import generate_db_test

from tests import app


@pytest.fixture()  # especially for performance you can define `scope='module'`
def db_test(app):
    with generate_db_test(app, 'test_integration_own_dataset', 'Beers'):
        yield app


def test_app(db_test):
    response = db_test.test_client().get('/beer/{}'.format(1))

    assert {'id': 1, 'name': 'Plzensky prazdroj'} == json.loads(response.data)
