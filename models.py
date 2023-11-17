from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Ticker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    last_updated = db.Column(db.String, nullable=False)
    data = db.Column(db.JSON)

    def __repr__(self):
        return f"<{self.name}>"
