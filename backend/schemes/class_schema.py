from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models.schedule_class import ScheduleClass


class ClassSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ScheduleClass
