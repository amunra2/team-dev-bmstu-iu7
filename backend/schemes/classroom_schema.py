from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models.classroom import Classroom

class ClassroomSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Classroom
