
import json
import pytest

from tests import app



def test_app(app):
    response = app.test_client().get('/beer/{}'.format(1))

    assert {'id': 1, 'name': 'Kozel'} == json.loads(response.data)
