from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ==============================
# User Model with Role
# ==============================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # student / teacher / parent / admin

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"


# ==============================
# Challenge Model
# ==============================
class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_blocks = db.Column(db.String(200), nullable=False)
    concept = db.Column(db.String(50))  # loop, condition, etc.
    difficulty = db.Column(db.String(20))  # easy, medium, hard
    json_template = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref='challenges', lazy=True)

    test_cases = db.relationship('TestCase', backref='challenge', lazy=True, cascade='all, delete-orphan')
    solution_templates = db.relationship('SolutionTemplate', backref='challenge', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Challenge {self.title} ({self.difficulty})>"
# ==============================
# Submission Model (Student Attempts)
# ==============================
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    code_json = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20))  # success / fail
    feedback_text = db.Column(db.Text)

    def __repr__(self):
        return f"<Submission student={self.student_id} challenge={self.challenge_id} result={self.result}>"


# ==============================
# Test Case Model
# ==============================
class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    input_data = db.Column(db.Text)
    expected_output = db.Column(db.Text)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<TestCase challenge={self.challenge_id}>"


# ==============================
# Solution Template Model
# ==============================
class SolutionTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    code_json = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<SolutionTemplate challenge={self.challenge_id} name={self.name}>"
