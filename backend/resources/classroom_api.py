from flask import jsonify, request

from flask_restful import Resource

from models.classroom import Classroom

from schemes.classroom_schema import ClassroomSchema

class ClassroomAPI(Resource):
    def get(self):
        schedule_class = request.args.get("class")

        building = request.args.get("building")
        floor = int(request.args.get("floor") or -1)

        fields = request.args.get("fields")
        fields = fields.split(',') if fields else fields
        schema = ClassroomSchema(only=fields)

        classrooms = Classroom.query.all()

        return jsonify([schema.dump(classroom) for classroom in classrooms])
