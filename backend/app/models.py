from app import db

class Criteria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)  # Cambiar de String a Text
    valid = db.Column(db.Boolean, default=False)
    cv_id = db.Column(db.Integer, db.ForeignKey('cv.id'), nullable=False)

class CV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    criteria = db.relationship('Criteria', backref='cv', lazy=True)
