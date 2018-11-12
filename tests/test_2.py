
import json

import pytest
from unittest.mock import patch, MagicMock

from . import app


@patch('hospudka.utils.pymysql')
def test_app(pymysql_conn, app):
    testing_data = {'id': 666, 'name': 'ostravar'}

    cursor = _load_cursor_mock(pymysql_conn, testing_data)

    response = app.test_client().get('/beer/{}'.format(testing_data['id']))

    assert testing_data == json.loads(response.data)

    cursor.execute.assert_called_with('SELECT `id`, `name` FROM Beers WHERE id={}'.format(testing_data['id']))


def _load_cursor_mock(pymysql_conn, return_data):
    connection = MagicMock()
    cursor = MagicMock()

    pymysql_conn.connect.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    cursor.fetchone.return_value = return_data

    return cursor
