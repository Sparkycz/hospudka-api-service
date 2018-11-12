
from contextlib import contextmanager
import pymysql


def init_config(app):
    app.config.from_envvar('CONFIG')


@contextmanager
def context_db_cursor(config):
    connection = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **config)

    with connection.cursor() as cursor:
        yield cursor

    connection.close()

