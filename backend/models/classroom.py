from database import db


class Classroom(db.Model):
    __tablename__ = "classrooms"

    classroom_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building = db.Column(db.String())
    floor = db.Column(db.Integer)
    number = db.Column(db.String())

    def __repr__(self):
        return (
            f"Classroom\n"
            f"id:       {self.classroom_id}\n"
            f"building: {self.building}\n"
            f"floor:    {self.floor}\n"
            f"number:   {self.number}"
        )
