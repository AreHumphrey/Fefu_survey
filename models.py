from app import db


class Students(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String, nullable=False)
    group_name = db.Column(db.String, nullable=False)
    course = db.Column(db.Integer, nullable=False)
    achievements = db.relationship("Achievements", back_populates="student")


class Achievements(db.Model):
    achievement_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    achievement = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    attachment = db.Column(db.BLOB)

    student = db.relationship("Students", back_populates="achievements")
