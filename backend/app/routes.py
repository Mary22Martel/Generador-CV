from flask import Blueprint, request, jsonify
from app.models import db, CV

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return jsonify({"message": "API funcionando correctamente."})


# Endpoint para subir un CV
@main_routes.route('/upload-cv', methods=['POST'])
def upload_cv():
    data = request.get_json()
    if not data.get('filename') or not data.get('content'):
        return jsonify({"error": "Filename and content are required"}), 400

    new_cv = CV(filename=data['filename'], content=data['content'])
    db.session.add(new_cv)
    db.session.commit()
    return jsonify({"message": "CV uploaded successfully!"}), 201

# Endpoint para listar cv   
@main_routes.route('/get-cvs', methods=['GET'])
def get_cvs():
    cvs = CV.query.all()  # Obtiene todos los CVs de la base de datos
    return jsonify([{"id": cv.id, "filename": cv.filename} for cv in cvs])
