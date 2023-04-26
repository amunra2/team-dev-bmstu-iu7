from database import db


class ScheduleClass(db.Model):
    __tablename__ = "classes"

    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    week = db.Column(db.Integer)
    day = db.Column(db.Integer)
    time = db.Column(db.Integer)

    states = db.relationship("State", back_populates="schedule_class")

    def __repr__(self):
        return (
            f"Shedule Class\n"
            f"id:   {self.class_id}\n"
            f"week: {self.week}\n"
            f"day:  {self.day}\n"
            f"time: {self.time}"
        )
