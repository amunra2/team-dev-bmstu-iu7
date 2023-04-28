from flask import jsonify

from flask_restful import Resource

from models.classroom import Classroom

from schemes.classroom_schema import ClassroomSchema

class ClassroomAPI(Resource):
    def get(self):
        self.classroom_schema = ClassroomSchema(only=('number',))
        classrooms = Classroom.query.all()
        return jsonify([self.classroom_schema.dump(classroom)
                        for classroom in classrooms])
