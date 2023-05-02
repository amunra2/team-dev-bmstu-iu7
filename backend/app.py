from dotenv import load_dotenv

from flasgger import Swagger

from flask import Flask

from flask_migrate import Migrate

from flask_restful import Api

from sqlalchemy import text

from database import db, init_db

from resources.class_api import ClassAPI
from resources.classroom_api import ClassroomAPI
from resources.state_api import StateAPI


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JSON_AS_ASCII'] = False

init_db(app)
migrate = Migrate(app, db)

api = Api(app)
api.add_resource(ClassroomAPI, "/classrooms", endpoint="classrooms_get_all")
api.add_resource(ClassroomAPI, "/classrooms/<int:classroom_id>", endpoint="classrooms_get_by_id")
api.add_resource(ClassAPI, "/classes", endpoint="classes_get_all")
api.add_resource(ClassAPI, "/classes/<int:class_id>", endpoint="classes_get_by_id")
api.add_resource(StateAPI, "/classrooms/<int:classroom_id>/classes/<int:class_id>",
                 endpoint="states")

app.config['SWAGGER'] = {'title': 'BMSTU FREE API'}
swagger = Swagger(app)


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
