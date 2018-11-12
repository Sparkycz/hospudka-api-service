import json
from flask import Flask

from .utils import init_config, context_db_cursor


def create_app():
    app = Flask(__name__)

    init_config(app)

    @app.route('/beer/<beer_id>')
    def get_beer(beer_id):
        with context_db_cursor(app.config['DATABASE']) as cursor:
            cursor.execute(f"SELECT `id`, `name` FROM Beers WHERE id={beer_id}")

            beer = cursor.fetchone()

        return json.dumps(beer)

    return app
