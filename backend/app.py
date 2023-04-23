from dotenv import load_dotenv

from flask import Flask

from flask_migrate import Migrate

from sqlalchemy import text

from database import db, init_db

app = Flask(__name__)
init_db(app)
migrate = Migrate(app, db)


@app.route('/')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return "Connection successful"
    except Exception as e:
        return f'Connection failed: {e}'


if __name__ == "__main__":
    load_dotenv()

    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)