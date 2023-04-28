from flask import jsonify, request

from flask_restful import Resource

from models.classroom import Classroom

from schemes.classroom_schema import ClassroomSchema

class ClassroomAPI(Resource):
    def get(self):
        schedule_class = request.args.get("class")

        building = request.args.get("building")
        floor = request.args.get("floor")

        fields = request.args.get("fields")
        fields = fields.split(',') if fields else fields
        schema = ClassroomSchema(only=fields)

        classrooms = Classroom.query

        if building:
            classrooms = classrooms.filter_by(building=building)

        if floor:
            classrooms = classrooms.filter_by(floor=int(floor))

        classrooms = classrooms.all()

        return jsonify([schema.dump(classroom) for classroom in classrooms])
