from app import db


# Abstract Models
class Abstract_Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    
    
class Abstract_ClassType(Abstract_Base):
    __abstract__ = True
    code = db.Column(db.String(10))
    start_time = db.Column(db.String(20), default=db.func.now())
    end_time = db.Column(db.String(20), default=db.func.now())
    day_one = db.Column(db.String(1))
    day_two = db.Column(db.String(1))


class Abstract_Course(Abstract_Base):
    __abstract__ = True
    program = db.Column(db.String(4))
    credits = db.Column(db.Float(4))
    number = db.Column(db.String(3))
    name = db.Column(db.String(50))
