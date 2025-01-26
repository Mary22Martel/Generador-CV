import os
from flask import Blueprint, request, jsonify, send_file
from app.models import db, CV, Criteria
import json
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import pdfplumber
import re
from fpdf import FPDF

# Inicializar las categorías y palabras clave
CATEGORY_KEYWORDS = {
    "Datos Personales": ["nombre", "dirección", "teléfono", "correo electrónico", "foto", "perfil personal"],
    "Grado de Instrucción": ["grado de instrucción", "nivel académico", "doctorado", "maestría", "licenciatura", "diplomado"],
    "Experiencia Laboral": ["experiencia laboral", "trabajo", "proyectos de ingeniería", "empleos previos"],
    "Idiomas": ["idioma", "inglés", "español", "nivel avanzado", "nivel intermedio", "multilingüe"],
    "Certificaciones": ["certificación", "certificado", "curso avanzado", "AWS", "Azure", "Scrum", "PMP"],
    "Conocimientos de Programación y Desarrollo": ["programación", "desarrollo", "lenguajes de programación", "Python", "Java", "frameworks"],
    "Habilidades Técnicas y Digitales": ["habilidades técnicas", "competencias digitales", "herramientas digitales", "ofimática", "Scrum", "Kanban"],
    "Competencias Digitales": ["herramientas digitales", "ofimática", "Excel", "PowerPoint"],
    "Proyectos": ["proyectos", "portafolio", "github", "proyectos personales"],
    "Habilidades Blandas": ["habilidad blanda", "soft skills", "liderazgo", "trabajo en equipo", "comunicación"],
    "Habilidades Técnicas": ["habilidad técnica", "hard skills", "tecnologías", "lenguajes de programación"]
}

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
            with pdfplumber.open(file_path) as pdf:
                extracted_text = " ".join([page.extract_text() for page in pdf.pages])
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

    return jsonify({"message": "CV uploaded successfully!", "cv_id": cv.id}), 201

# Endpoint para listar CVs
@main_routes.route('/get-cvs', methods=['GET'])
def get_cvs():
    cvs = CV.query.all()
    return jsonify([{"id": cv.id, "filename": cv.filename} for cv in cvs])

# Endpoint para extraer criterios de un CV
@main_routes.route('/extract-criteria/<int:cv_id>', methods=['POST'])
def extract_criteria(cv_id):
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({"error": "CV not found"}), 404

    text = cv.content or ""
    detected_categories = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                if category not in detected_categories:
                    detected_categories[category] = []
                detected_categories[category].append({
                    "description": f"Se detectó la categoría '{category}' en el CV.",
                    "cv_id": cv.id
                })
                break

    for category, criteria_list in detected_categories.items():
        for crit in criteria_list:
            new_criteria = Criteria(
                description=crit["description"],
                cv_id=crit["cv_id"]
            )
            db.session.add(new_criteria)

    db.session.commit()

    return jsonify({
        "message": "Criteria extracted and classified successfully!",
        "criteria": detected_categories
    })

# Endpoint para extraer criterios de todos los CVs
@main_routes.route('/extract-criteria-all', methods=['POST'])
def extract_criteria_all():
    cvs = CV.query.all()
    if not cvs:
        return jsonify({"error": "No CVs found"}), 404

    all_detected_categories = {}
    for cv in cvs:
        text = cv.content or ""
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    if category not in all_detected_categories:
                        all_detected_categories[category] = []
                    all_detected_categories[category].append({
                        "description": f"Se detectó la categoría '{category}' en el CV {cv.filename}.",
                        "cv_id": cv.id
                    })
                    break

    for category, criteria_list in all_detected_categories.items():
        for crit in criteria_list:
            new_criteria = Criteria(
                description=crit["description"],
                cv_id=crit["cv_id"]
            )
            db.session.add(new_criteria)

    db.session.commit()

    return jsonify({
        "message": "Criteria extracted and classified successfully for all CVs!",
        "criteria": all_detected_categories
    })

# Endpoint para listar criterios agrupados
@main_routes.route('/get-criteria', methods=['GET'])
def get_criteria():
    criteria = Criteria.query.all()
    grouped_criteria = {category: [] for category in CATEGORY_KEYWORDS.keys()}
    for crit in criteria:
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword.lower() in crit.description.lower() for keyword in keywords):
                grouped_criteria[category].append({
                    "id": crit.id,
                    "cv_id": crit.cv_id,
                    "description": crit.description,
                    "valid": crit.valid
                })
                break

    cleaned_criteria = {k: v for k, v in grouped_criteria.items() if v}
    return jsonify(cleaned_criteria)

# Endpoint para votar criterios
@main_routes.route('/vote-criteria/<int:criteria_id>', methods=['PATCH'])
def vote_criteria(criteria_id):
    criteria = Criteria.query.get(criteria_id)
    if not criteria:
        return jsonify({"error": "Criteria not found"}), 404

    data = request.get_json()
    if "valid" not in data:
        return jsonify({"error": "Missing 'valid' field in request body"}), 400

    criteria.valid = data["valid"]
    db.session.commit()

    return jsonify({
        "message": "Criteria updated successfully",
        "criteria_id": criteria.id,
        "valid": criteria.valid
    })

# Endpoint para generar un CV
from fpdf import FPDF

@main_routes.route('/generate-cv', methods=['GET'])
def generate_cv():
    # Obtener todos los criterios válidos
    valid_criteria = Criteria.query.filter_by(valid=True).all()

    if not valid_criteria:
        return jsonify({"error": "No valid criteria found"}), 404

    # Crear un PDF con los criterios válidos
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título del documento
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Nuevo Formato de CV", ln=True, align='C')
    pdf.ln(10)  # Salto de línea

    # Subtítulo
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Basado en los criterios válidos extraídos", ln=True, align='C')
    pdf.ln(15)

    # Crear una tabla con los criterios
    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(200, 220, 255)  # Color de fondo para la cabecera
    pdf.cell(90, 10, "Categoría", border=1, align='C', fill=True)
    pdf.cell(100, 10, "Descripción", border=1, align='C', fill=True)
    pdf.ln()

    for crit in valid_criteria:
        # Extraer la categoría de la descripción
        category = None
        for cat in CATEGORY_KEYWORDS.keys():
            if cat in crit.description:
                category = cat
                break
        category = category or "Sin Categoría"  # Fallback si no hay categoría exacta

        # Agregar fila a la tabla
        pdf.cell(90, 10, category, border=1, align='L')
        pdf.cell(100, 10, crit.description[:50] + "...", border=1, align='L')  # Limitar descripción a 50 caracteres
        pdf.ln()

    # Guardar el PDF en un string binario
    pdf_output = pdf.output(dest='S').encode('latin1')

    # Escribir el PDF en un objeto BytesIO
    memory_file = BytesIO()
    memory_file.write(pdf_output)
    memory_file.seek(0)

    # Enviar el PDF como respuesta
    return send_file(
        memory_file,
        download_name="nuevo_formato_cv.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )


# Endpoint para reiniciar datos
@main_routes.route('/reset', methods=['POST'])
def reset_data():
    try:
        db.session.query(Criteria).delete()
        db.session.query(CV).delete()
        db.session.commit()

        uploads_folder = 'uploads'
        if os.path.exists(uploads_folder):
            for file in os.listdir(uploads_folder):
                file_path = os.path.join(uploads_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        return jsonify({"message": "Datos y archivos limpiados correctamente."}), 200
    except Exception as e:
        return jsonify({"error": "Error al limpiar los datos", "details": str(e)}), 500
