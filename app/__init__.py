from flask import Flask


def create_app():
    app = Flask(__name__, template_folder="templates")

    from app.routes.main import main
    from app.routes.strategy import strategy

    app.register_blueprint(main)
    app.register_blueprint(strategy)

    return app
