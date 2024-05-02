from flask import Flask
from stock_ticker import models
from stock_ticker import routes


app = Flask(__name__)


def init_config():
    app.register_blueprint(blueprint=routes.view_routes)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    models.db.init_app(app)
    with app.app_context():
        # models.db.drop_all()
        models.db.create_all()


if __name__ == "__main__":
    init_config()
    app.run(debug=True)
