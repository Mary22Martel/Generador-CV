import os
from flask import Blueprint, request, jsonify
from app.models import db, CV, Criteria
import json
from flask import send_file
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document



main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return jsonify({"message": "API funcionando correctamente."})


# Endpoint para subir un CV
@main_routes.route('/upload-cv', methods=['POST'])
def upload_cv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Guardar el archivo en una carpeta temporal
    temp_dir = "uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)

    # Extraer texto según el tipo de archivo
    extracted_text = ""
    if file.filename.endswith('.pdf'):
        try:
            pdf_reader = PdfReader(file_path)
            extracted_text = " ".join([page.extract_text() for page in pdf_reader.pages])
        except Exception as e:
            return jsonify({"error": "Failed to process PDF", "details": str(e)}), 500

    elif file.filename.endswith('.docx'):
        try:
            doc = Document(file_path)
            extracted_text = " ".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return jsonify({"error": "Failed to process Word file", "details": str(e)}), 500
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    # Guardar los datos en la base de datos
    cv = CV(filename=file.filename, content=extracted_text)
    db.session.add(cv)
    db.session.commit()

    # Eliminar archivo temporal
    os.remove(file_path)

    return jsonify({"message": "CV uploaded successfully!", "cv_id": cv.id}), 201

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

#generar nuevo fromato
@main_routes.route('/generate-cv', methods=['GET'])
def generate_cv():
    # Obtener todos los criterios válidos
    valid_criteria = Criteria.query.filter_by(valid=True).all()

    if not valid_criteria:
        return jsonify({"error": "No valid criteria found"}), 404

    # Crear un formato básico de CV (JSON simulado)
    cv_data = {
        "sections": [
            {"title": "Criteria", "content": [crit.description for crit in valid_criteria]}
        ]
    }

    # Simulación: Guardar como JSON
    json_data = json.dumps(cv_data, indent=4)

    # Crear un archivo en memoria para devolverlo
    memory_file = BytesIO()
    memory_file.write(json_data.encode('utf-8'))
    memory_file.seek(0)

    return send_file(
        memory_file,
        download_name="generated_cv.json",
        as_attachment=True,
        mimetype='application/json'
    )