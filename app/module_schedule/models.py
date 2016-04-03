from app import db
from flask import current_app
from app.abstract_models import Abstract_Base, Abstract_ClassType, Abstract_Course
from app.module_authentication.models import User


# Concrete Models
class Student(Abstract_Base):
    __tablename__ = 'students'
    full_name = db.Column(db.String(50), index = True)
    academic_record = db.Column(db.Integer, db.ForeignKey('academic_records.id'))
    sequence = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    user = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, full_name=None, academic_record=None, sequence=None, user=None):
        self.full_name = full_name
        self.academic_record = academic_record
        self.sequence = sequence
        self.user = user

    def get_lectures():
        registered_lectures = []
        academic_records = db.session.query(AcademicRecord).filter_by(user_id=session['user_id'], lecture_status='registered').all()
        for ac in academic_records:
            registered_lectures.append(db.session.query(Lecture).filter_by(id=ac.lecture_id).first())
        if(current_app):
            return registered_lectures

    def get_labs():
        labs = []
        lectures = self.get_lectures()

        for lecture in lectures:
            labs_query = db.session.query(Lab).filter_by(lecture_id=lecture_id).all()
            for lab in labs_query:
                labs.append(lab)

        if(current_app):
            return labs

    def get_tutorials():
        tutorials = []
        lectures = self.get_lectures()

        for lecture in lectures:
            tutorials_query = db.session.query(Tutorial).filter_by(lecture_id=lecture_id).all()
            for tutorial in tutorials_query:
                tutorials.append(tutorial)

        if(current_app):
            return tutorials


    def register_lecture(lecture_id):
        lecture = db.session.query(Lecture).filter_by(id=lecture_id).first()
        mappings = db.session.query(Mapping).filter_by(course_id=lecture.course_id).all()
        prerequisites = []
        for mapping in mappings:
            prerequisites.append(db.session.query(Course).filter_by(id=mapping.course_req_id).first())

        for prerequisite in prerequisites:
            if not self.completed_course(prerequisite.id):
                return False

        db.session.add(AcademicRecord(session['user_id'], lecture_id, 'registered'))
        db.session.commit()
        return True

    def completed_course(course_id):
        academic_records = db.session.query(AcademicRecord).filter_by(user_id=session['user_id'], lecture_status='completed').all()
        for ac in academic_records:

            lecture = db.session.query(Lecture).filter_by(id=ac.lecture_id).first()
            completed_course = db.session.query(Course).filter_by(id=lecture.course_id).first()
            query_course = db.session.query(Course).filter_by(id=course_id).first()

            if completed_course == query_course:
                return True

        return False

    def __repr__(self):
        return '<User %r>' % (self.full_name)


class Course(Abstract_Course):
    __tablename__ = 'courses'
    requisite = db.Column(db.Integer, db.ForeignKey('mappings.id'))
    lectures = db.relationship("Lecture")

    def __init__(self, program=None, credits=None, number=None, name=None):
        self.program = program
        self.credits = credits
        self.number = number
        self.name = name

    def get_lectures():
        return db.session.query(Lecture).filter_by(course_id=self.id).all()

    def __repr__(self):
        return '<Course %r>' % (self.name)

    def serialize(self):
        return {
            'name': self.name,
            'program': self.program,
            'number': self.number,
            'credits': credits
        }


class Lab(Abstract_ClassType):
    __tablename__ = 'labs'
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))

    def __init__(self, lecture_id=None, section_code=None, start_time=None, end_time=None, day_one=None):
        self.lecture_id = lecture_id
        self.section_code = section_code
        self.start_time = start_time
        self.end_time = end_time
        self.day_one = day_one

    def __repr__(self):
        return '<Lab %r>' % (self.code)


class Tutorial(Abstract_ClassType):
    __tablename__ = 'tutorials'
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))

    def __init__(self, lecture_id=None, section_code=None, start_time=None, end_time=None, day_one=None, day_two=None):
        self.lecture_id = lecture_id
        self.section_code = section_code
        self.start_time = start_time
        self.end_time = end_time
        self.day_one = day_one
        self.day_two = day_two

    def __repr__(self):
        return '<Tutorial %r>' % (self.code)


class Lecture(Abstract_ClassType):
    __tablename__ = 'lectures'
    instructor = db.Column(db.String(50))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'))

    tutorial = db.relationship("Tutorial")
    lab = db.relationship("Lab")

    def __init__(self, instructor=None, course_id=None, semester_id=None, start_time=None, end_time=None, day_one=None, day_two=None):
        self.instructor = instructor
        self.course_id = course_id
        self.semester_id = semester_id
        self.start_time = start_time
        self.end_time = end_time
        self.day_one = day_one
        self.day_two = day_two

    def serialize(self):
        course = self.get_course()
        return {
            'name': course.name,
            'program': course.program,
            'number': course.number,
            'credits': course.credits,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'instructor': self.instructor
        }

    def get_tutorials(self):
        return db.session.query(Tutorial).filter_by(lecture_id=self.id).all()

    def get_course(self):
        return db.session.query(Course).filter_by(id=self.course_id).first()

    def __repr__(self):
        return '<Lecture %r>' % (self.instructor)


class AcademicRecord(Abstract_Base):
    __tablename__ = 'academic_records'
    user_id = db.Column(db.Integer)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))
    lecture_status = db.Column(db.String(50))

    def __init__(self, user_id=None, lecture_id=None, lecture_status=None):
        self.user_id = user_id
        self.lecture_id = lecture_id
        self.lecture_status = lecture_status

    def __repr__(self):
        return '<AcademicRecord %r>' % (self.id)


class Semester(Abstract_Base):
    __tablename__ = 'semesters'
    semester_id = db.Column(db.String(50))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))

    def __init__(self, semester_id=None, lecture_id=None):
        self.semester_id = semester_id
        self.lecture_id = lecture_id

    def __repr__(self):
        return '<Semester %r>' % (self.id)


class Sequence(Abstract_Base):
    __tablename__ = 'sequences'
    option = db.Column(db.String(50))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    def __init__(self, option=None, course_id=None):
        self.option = option
        self.course_id = course_id

    def __repr__(self):
        return '<Sequence %r>' % (self.id)


class Mapping(Abstract_Base):
    __tablename__ = 'mappings'
    course_req_id = db.Column(db.Integer)
    course_req_type = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    def __init__(self, course_req_id=None, course_req_type=None, course_id=None):
        self.course_req_id = course_req_id
        self.course_req_type = course_req_type
        self.course_id = course_id

    def __repr__(self):
        return '<Mapping %r>' % (self.id)


class Elective(Abstract_Base):
    __tablename__ = 'electives'
    elective_type = db.Column(db.String(50))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    def __init__(self, elective_type=None, course_id=None):
        self.elective_type = elective_type
        self.course_id = course_id

    def __repr__(self):
        return '<Elective %r>' % (self.id)

