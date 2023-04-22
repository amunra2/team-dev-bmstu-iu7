from database import db

class Class(db.Model):
    __tablename__ = "classes"

    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    week = db.Column(db.Integer)
    day = db.Column(db.Integer)
    time = db.Column(db.Integer)

    def __repr__(self):
        return (
            f"Class\n"
            f"id:   {self.class_id}\n"
            f"week: {self.week}\n"
            f"day:  {self.day}\n"
            f"time: {self.time}"
        )
