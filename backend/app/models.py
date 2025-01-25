from app import db

# Modelo para los CVs subidos
class CV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Nombre del archivo
    content = db.Column(db.Text, nullable=False)  # Contenido del CV

# Modelo para los criterios extraídos
class Criteria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)  # Descripción del criterio
    valid = db.Column(db.Boolean, default=False)  # Si el criterio es válido o no