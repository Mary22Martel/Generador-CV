import os
from flask import Blueprint, request, jsonify
from app.models import db, CV, Criteria
import json
from flask import send_file
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import pdfplumber
import spacy
import re



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

    return jsonify({"message": "CV uploaded successfully!", "cv_id": cv.id}), 201


# Endpoint para listar cv   
@main_routes.route('/get-cvs', methods=['GET'])
def get_cvs():
    cvs = CV.query.all()  # Obtiene todos los CVs de la base de datos
    return jsonify([{"id": cv.id, "filename": cv.filename} for cv in cvs])

# Endpoint para extraer texto 
@main_routes.route('/process-cvs', methods=['POST'])
def process_cvs():
    cvs = CV.query.all()
    results = []

    for cv in cvs:
        file_path = os.path.join('uploads', cv.filename)
        if not os.path.exists(file_path):
            results.append({"error": f"File not found: {file_path}"})
            continue

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Extraer texto y tablas
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            # Procesar filas relevantes
                            if any("Puntaje" in str(cell) for cell in row):
                                results.append({"table_row": row})

        except Exception as e:
            results.append({"error": str(e)})

    return jsonify(results)


# Endpoint para extraer criterios   
# Cargar el modelo spaCy
nlp = spacy.load("es_core_news_sm")

@main_routes.route('/extract-criteria/<int:cv_id>', methods=['POST'])
def extract_criteria(cv_id):
    # Buscar el CV por ID
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({"error": "CV not found"}), 404

    # Contenido del CV
    text = cv.content

    # Limpieza inicial para eliminar encabezados y pie de página
    text = re.sub(r"(?i)formato de evaluación.*?mínimos a evaluar", "", text, flags=re.S)
    text = re.sub(r"(?i)punta?je total.*?condición", "", text, flags=re.S)
    text = re.sub(r"(?i)firma de representante.*", "", text, flags=re.S)

    # Palabras clave para detectar bloques relevantes
    KEYWORDS = [
        "Experiencia Laboral", "Habilidades", "Certificaciones", 
        "Educación", "Idiomas", "Proyectos"
    ]

    # Procesar texto con spaCy
    doc = nlp(text)
    extracted_criteria = []

    for sent in doc.sents:
        sentence = sent.text.strip()

        # Filtrar contenido relevante: debe contener al menos una palabra clave
        if any(keyword.lower() in sentence.lower() for keyword in KEYWORDS) and len(sentence) > 20:
            extracted_criteria.append({
                "description": sentence,
                "cv_id": cv.id
            })

    # Eliminar duplicados por descripción
    unique_criteria = {crit["description"]: crit for crit in extracted_criteria}.values()

    # Guardar criterios válidos en la base de datos
    for crit in unique_criteria:
        new_criteria = Criteria(description=crit["description"], cv_id=crit["cv_id"])
        db.session.add(new_criteria)

    db.session.commit()

    return jsonify({
        "message": "Criteria extracted and cleaned successfully!",
        "criteria": list(unique_criteria)
    })




#listar criterios
@main_routes.route('/get-criteria', methods=['GET'])
def get_criteria():
    # Obtener todos los criterios de la base de datos
    criteria = Criteria.query.all()

    # Inicializar diccionario para agrupar criterios por categoría
    grouped_criteria = {
        "Certificaciones": [],
        "Educación": [],
        "Experiencia Laboral": [],
        "Habilidades": [],
        "Idiomas": [],
        "Proyectos": []
    }

    # Palabras clave para cada categoría
    category_keywords = {
        "Certificaciones": ["certificación", "certificado", "curso", "diploma"],
        "Educación": ["grado", "título", "universitario", "egresado"],
        "Experiencia Laboral": ["experiencia", "trabajo", "proyecto"],
        "Habilidades": ["habilidad", "soft skill", "hard skill", "comunicación", "liderazgo"],
        "Idiomas": ["idioma", "lenguaje", "inglés", "bilingüe"],
        "Proyectos": ["proyecto", "portafolio", "github", "desarrollo"]
    }

    # Conjunto para rastrear descripciones únicas y evitar duplicados
    seen_descriptions = set()

    # Limpiar y clasificar criterios
    for crit in criteria:
        # Convertir descripción a minúsculas y eliminar espacios en blanco al inicio y final
        description = crit.description.strip().lower()

        # Filtros: eliminar texto irrelevante o descripciones muy cortas
        if (
            "formato de evaluación curricular" in description
            or len(description) < 15  # Descripciones muy cortas no son útiles
            or "total puntaje" in description
            or "condición" in description
        ):
            continue

        # Evitar duplicados
        if description in seen_descriptions:
            continue
        seen_descriptions.add(description)

        # Clasificar por categoría usando palabras clave
        added = False
        for category, keywords in category_keywords.items():
            if any(keyword in description for keyword in keywords):
                grouped_criteria[category].append({
                    "id": crit.id,
                    "cv_id": crit.cv_id,
                    "description": crit.description,
                    "valid": crit.valid
                })
                added = True
                break

        # Ignorar descripciones que no encajan en ninguna categoría
        if not added:
            continue

    # Filtrar categorías vacías para devolver sólo las que contienen datos
    cleaned_criteria = {k: v for k, v in grouped_criteria.items() if v}

    # Devolver el JSON con los criterios agrupados
    return jsonify(cleaned_criteria)











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

    # Estructurar el CV agrupando los criterios por categoría
    cv_data = {"sections": []}
    categories = ["Experiencia Laboral", "Idiomas", "Certificaciones", "Educación", "Habilidades", "Proyectos"]
    
    for category in categories:
        # Filtrar criterios que pertenecen a la categoría
        content = [crit.description for crit in valid_criteria if category in crit.description]
        if content:
            cv_data["sections"].append({"title": category, "content": content})

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



#limpiar todo
@main_routes.route('/reset', methods=['POST'])
def reset_data():
    try:
        # Eliminar todos los criterios
        db.session.query(Criteria).delete()
        # Eliminar todos los CVs
        db.session.query(CV).delete()
        db.session.commit()

        # Limpiar la carpeta de uploads
        uploads_folder = 'uploads'
        if os.path.exists(uploads_folder):
            for file in os.listdir(uploads_folder):
                file_path = os.path.join(uploads_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        return jsonify({"message": "Datos y archivos limpiados correctamente."}), 200
    except Exception as e:
        return jsonify({"error": "Error al limpiar los datos", "details": str(e)}), 500
