from flask import Blueprint, request, jsonify
from app.models import db, CV, Criteria


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

# Endpoint para extraer criterios   
@main_routes.route('/extract-criteria/<int:cv_id>', methods=['POST'])
def extract_criteria(cv_id):
    # Busca el CV por ID
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({"error": "CV not found"}), 404

    # Simular criterios de ejemplo
    fake_criteria = [
        "Strong communication skills",
        "Experience with Python",
        "Team leadership skills"
    ]
    
    # Insertar criterios simulados en la base de datos
    for description in fake_criteria:
        new_criteria = Criteria(description=description)
        db.session.add(new_criteria)

    db.session.commit()
    return jsonify({"message": "Criteria extracted successfully!"})


#listar criterios
@main_routes.route('/get-criteria', methods=['GET'])
def get_criteria():
    criteria = Criteria.query.all()
    return jsonify([{"id": crit.id, "description": crit.description, "valid": crit.valid} for crit in criteria])

#enpoint para votar criterios
@main_routes.route('/vote-criteria/<int:criteria_id>', methods=['PATCH'])
def vote_criteria(criteria_id):
    # Buscar el criterio por ID
    criteria = Criteria.query.get(criteria_id)
    if not criteria:
        return jsonify({"error": "Criteria not found"}), 404

    # Obtener la validación del cuerpo de la solicitud
    data = request.get_json()
    if "valid" not in data:
        return jsonify({"error": "Missing 'valid' field in request body"}), 400

    # Actualizar la validez del criterio
    criteria.valid = data["valid"]
    db.session.commit()

    return jsonify({
        "message": "Criteria updated successfully",
        "criteria_id": criteria.id,
        "valid": criteria.valid
    })
