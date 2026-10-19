import logging
import os
from flask import Flask

from .db import init_db
from .routes import bp


def create_app(db_path=None):
    app = Flask(__name__)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.config["DATABASE"] = db_path or os.path.join(base_dir, "complaints.db")

    logging.basicConfig(
        filename=os.path.join(base_dir, "app.log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    init_db(app.config["DATABASE"])
    app.register_blueprint(bp)
    return app
