import csv
import random
import re
import time
from contextlib import contextmanager

from pathlib import Path
import pymysql

RESOURCES_PATH = Path(__file__).parents[1] / 'resources'


def generate_db(db_config, resource_path, ddl_path, table_names, null_value = '#NULL#'):

    def prepare_database():
        """Creates testing database"""
        cursor.execute('CREATE DATABASE ' + database)
        cursor.execute('USE ' + database)
        cursor.execute('SET foreign_key_checks = 0')
        # Be strict as much as we can otherwise we can miss some error converted to warning etc.
        cursor.execute("SET SESSION SQL_MODE ='STRICT_ALL_TABLES,ONLY_FULL_GROUP_BY,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION'")
        # Just to be sure, it is enabled by default in versions >= 5.7.7
        cursor.execute('SET SESSION innodb_strict_mode=1')

    def create_sql_schema():
        """Creates SQL schema of certain tables."""
        for table in table_names:
            table_path = table + '.sql'
            sql = ddl_path / table_path
            sql = sql.read_text(encoding='utf-8')
            sql = re.sub(
                r'(\)\s+ENGINE=InnoDB\b.*)\bROW_FORMAT=DYNAMIC\b',
                r'\g<1>ROW_FORMAT=COMPACT',
                sql,
                1,
                re.I
            )
            cursor.execute(sql)

    def fill_data():
        """Fill data from CSV files into created tables."""
        for table in table_names:
            table_name = table + '.csv'
            file_path = resource_path / table_name
            if not file_path.is_file():
                continue

            _load_data_from_csv(table, file_path)

    def _connect_mysql(db_config):
        """
        Tries several times to connect that service to test MySQL
        Because the containers (this one and MySQL) are built at the same time, sometimes happen that
        the MySQL is not fully ready. In this state, it can accept connections but SQL queries are not executed, and
        it throws an exception. This code implements a very simple waiting mechanism which is used when
        this state is detected.
        """
        attempt = 0
        while True:
            try:
                conn = pymysql.connect(charset='utf8', **db_config)
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")

                return conn
            except pymysql.err.MySQLError:
                attempt += 1
                time.sleep(1)
                if attempt > 30:
                    raise
                continue

    def _load_data_from_csv(table_name, path_to_csv_file):
        """Loads dataset from CSV file and prepare SQL query for Insert that data into the testing DB."""
        with open(path_to_csv_file, newline='', encoding='utf-8') as csv_file:
            csv_data = csv.reader(csv_file, delimiter=',', quotechar='"')
            iter_csv_data = iter(csv_data)
            column_names = next(iter_csv_data)
            dataset_sql = __create_dataset_sql(table_name, column_names)
            for row in iter_csv_data:
                if not row:
                    continue
                if null_value:
                    new_row = []
                    for value in row:
                        if value == null_value:
                            value = None
                        new_row.append(value)
                else:
                    new_row = row

                cursor.execute(__create_values_sql(dataset_sql, new_row), new_row)
            connection.commit()

    def __create_dataset_sql(table_name, columns):
        """Creates SQL query for inserting testing data."""
        sql = 'INSERT INTO ' + table_name + '('
        column_names = [('`' + column + '`') for column in columns]
        sql += ','.join(column_names)
        sql += ') VALUES '
        return sql

    def __create_values_sql(dataset_sql, row):
        sql = dataset_sql + '('
        columns = ['%s' for column in row]
        sql += ','.join(columns)
        sql += ")"
        return sql

    connection = _connect_mysql(db_config)
    connection.cursorclass = pymysql.cursors.DictCursor
    cursor = connection.cursor()

    database = 'test_' + str(random.randrange(1, 3)) + "_" + str(time.time()).replace(".", "_")

    prepare_database()
    create_sql_schema()
    fill_data()

    return connection, database


def drop_db(connection, database):
    """Drops database from the testing DB."""
    connection.cursor().execute('DROP DATABASE ' + database)


@contextmanager
def generate_db_test(app, testcase_path, *args):
    db_config = app.config.get('DATABASE')

    connection, database = generate_db(db_config, RESOURCES_PATH / testcase_path, RESOURCES_PATH / testcase_path, args)

    app.config['DATABASE']['db'] = database

    yield app

    drop_db(connection, database)
    connection.close()
