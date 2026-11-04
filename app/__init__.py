"""Flask application factory for the workout tracking API."""
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///workouts.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models before registering routes so metadata is populated for migrations.
    from app import models  # noqa: F401
    from app.routes import api
    app.register_blueprint(api)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        return jsonify({"error": "The request conflicts with existing data or a database constraint."}), 409

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found."}), 404

    return app
