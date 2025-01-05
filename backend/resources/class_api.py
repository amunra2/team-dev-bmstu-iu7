from flasgger.utils import swag_from

from flask import jsonify, request

from flask_restful import Resource

from database import db

from models.schedule_class import ScheduleClass

from schemes.class_schema import ClassSchema


class ClassAPI(Resource):
    @swag_from('../swagger/classes_get_all.yml', endpoint='classes_get_all')
    @swag_from('../swagger/classes_get_by_id.yml', endpoint='classes_get_by_id')
    def get(self, class_id=None):
        fields = request.args.get("fields")
        fields = fields.split(',') if fields else fields
        schema = ClassSchema(only=fields)

        if class_id is not None:
            schedule_class = ScheduleClass.query.get(class_id)
            return jsonify(schema.dump(schedule_class))

        week = request.args.get("week")
        day = request.args.get("day")
        time = request.args.get("time")

        classes = self._get_by_params(week, day, time)

        return jsonify([schema.dump(schedule_class) for schedule_class in classes])

    @swag_from('../swagger/classes_post.yml', endpoint='classes_get_all')
    def post(self):
        fields = request.args.get("fields")
        fields = fields.split(',') if fields else fields
        schema = ClassSchema(only=fields)

        class_json = request.json
        week = class_json["week"]
        day = class_json["day"]
        time = class_json["time"]

        schedule_class = ScheduleClass.query.filter_by(week=week, day=day, time=time).first()

        if schedule_class:
            return jsonify(schema.dump(schedule_class))

        new_class = ScheduleClass(week=week, day=day, time=time)

        db.session.add(new_class)
        db.session.commit()

        return jsonify(schema.dump(new_class))

    @swag_from('../swagger/classes_delete.yml', endpoint='classes_get_all')
    def delete(self):
        deleted_number = db.session.query(ScheduleClass).delete()
        db.session.commit()

        return deleted_number

    def _get_by_params(self, week, day, time):
        classes = ScheduleClass.query

        if week:
            classes = classes.filter_by(week=int(week))

        if day:
            classes = classes.filter_by(day=int(day))

        if time:
            classes = classes.filter_by(time=int(time))

        return classes.all()
