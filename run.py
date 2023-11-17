from flask import Flask
from models import db
from routes import view_routes


app = Flask(__name__)
# !https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tesco&apikey=demo
# !https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=demo


def init_config():
    app.register_blueprint(blueprint=view_routes)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        # db.drop_all()
        db.create_all()


if __name__ == "__main__":
    init_config()
    app.run(debug=True)
