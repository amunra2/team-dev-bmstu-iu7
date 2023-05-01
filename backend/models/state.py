from database import db


class State(db.Model):
    __tablename__ = "states"

    classroom_id = db.Column(db.Integer,
                             db.ForeignKey("classrooms.classroom_id", ondelete="CASCADE"),
                             primary_key=True)
    class_id = db.Column(db.Integer,
                         db.ForeignKey("classes.class_id", ondelete="CASCADE"),
                         primary_key=True)
    state = db.Column(db.Boolean, default=False)

    classroom = db.relationship("Classroom", back_populates="states", cascade="delete")
    schedule_class = db.relationship("ScheduleClass", back_populates="states", cascade="delete")

    def __repr__(self):
        str_state = "FREE" if self.state else "OCCUPIED"
        return (
            f"State\n"
            f"classroom_id: {self.classroom_id}\n"
            f"class_id:     {self.class_id}\n"
            f"state:        {str_state}"
        )
