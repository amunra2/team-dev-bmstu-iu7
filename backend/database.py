from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app, db_connection):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_connection
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
