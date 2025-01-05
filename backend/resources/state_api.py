from flasgger.utils import swag_from

from flask import jsonify

from flask_restful import Resource

from database import db

from models.state import State

from schemes.state_schema import StateSchema


class StateAPI(Resource):
    @swag_from('../swagger/states_post.yml', endpoint='states')
    def post(self, classroom_id, class_id):
        schema = StateSchema()

        state = State.query.filter_by(classroom_id=classroom_id, class_id=class_id).first()

        if state:
            return jsonify(schema.dump(state))

        new_state = State(classroom_id=classroom_id, class_id=class_id)

        db.session.add(new_state)
        db.session.commit()

        return jsonify(schema.dump(new_state))
