"""Summary: Application Configurator

Creates an application instance that registers all the project's blueprints
"""
from flask import Flask, Response, redirect, render_template, url_for
from flask.logging import create_logger
from app.routes.blueprints import sweep_api_v1


def create_application() -> Flask:
    """
    :return: Flask application instance
    """
    application = Flask(__name__, template_folder='build/templates')

    application.register_blueprint(sweep_api_v1)

    logger = create_logger(application)

    @application.route('/')
    def home():
        return render_template('home.html')

    @application.errorhandler(404)
    def page_not_found(error) -> Response:
        logger.error(error)
        return redirect(url_for('home'))

    return application
