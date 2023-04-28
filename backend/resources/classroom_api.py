import json

from flask import jsonify, request

from flask_restful import Resource

from models.classroom import Classroom
from models.schedule_class import ScheduleClass
from models.state import State

from schemes.classroom_schema import ClassroomSchema

class ClassroomAPI(Resource):
    def get(self):
        is_free_mode = (request.args.get("is_free") == "true")

        if is_free_mode:
            number = request.args.get("number")
            schedule_class = request.args.get("class")
            week, day, time = map(int, schedule_class.split(','))

            classroom_id = Classroom.query.filter_by(number=number).with_entities(Classroom.classroom_id)
            schedule_class_id = ScheduleClass.query\
                                .filter_by(week=week, day=day, time=time)\
                                .with_entities(ScheduleClass.class_id)

            in_states = State.query.filter_by(classroom_id=classroom_id, class_id=schedule_class_id).all()

            answer = { "is_free" : False if in_states else True }

            return jsonify(answer)

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

        if schedule_class:
            week, day, time = map(int, schedule_class.split(','))

            schedule_class = ScheduleClass.query\
                                .filter_by(week=week, day=day, time=time)\
                                .with_entities(ScheduleClass.class_id)

            occupied_classrooms_ids = State.query.filter_by(class_id=schedule_class).with_entities(State.classroom_id)

            classrooms = classrooms.filter(Classroom.classroom_id.not_in(occupied_classrooms_ids))

        classrooms = classrooms.all()

        return jsonify([schema.dump(classroom) for classroom in classrooms])
