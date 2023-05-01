from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models.state import State


class StateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = State
        include_relationships = True
