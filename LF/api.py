# Importar las bibliotecas necesarias
from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF para parsear archivos PDF
import re  # Expresiones regulares para la coincidencia de patrones
import json  # Para trabajar con datos JSON
import pandas as pd

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configurar la carpeta de carga para almacenar los archivos subidos
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crear la carpeta si no existe
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Almacenar la configuración de la carpeta de carga

# Función para extraer texto de diferentes tipos de archivos
def extract_text_from_file(file_path):
    """Extrae texto de varios tipos de archivos."""
    ext = os.path.splitext(file_path)[-1].lower()  # Obtener la extensión del archivo en minúsculas
    
    if ext == ".pdf":
        # Si el archivo es un PDF, usar PyMuPDF (fitz) para extraer el texto
        with fitz.open(file_path) as pdf:
            return "".join(page.get_text() for page in pdf)
    
    elif ext in [".txt", ".log"]:
        # Si el archivo es un archivo de texto o log, leer su contenido
        print("txt")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    elif ext == ".csv":
        # Si el archivo es un CSV, usar pandas para leerlo y convertirlo a cadena
        print("csv")
        df = pd.read_csv(file_path)
        return df.to_string(index=False)
    
    else:
        return ""  # Retornar cadena vacía si el tipo de archivo no es compatible

# Ruta para la página principal, renderiza la plantilla HTML
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para procesar los archivos subidos
@app.route('/process', methods=['POST'])
def process_files():
    # Obtener la lista de archivos subidos y cualquier secuencia personalizada del formulario
    files = request.files.getlist('files[]')
    custom_sequence = request.form.get('custom_sequence', '')

    # Si no se subieron archivos, retornar una respuesta de error
    if not files:
        return jsonify({'error': 'No se subieron archivos'}), 400

    consolidated_text = ""  # Variable para almacenar el texto de todos los archivos

    # Recorrer todos los archivos subidos, guardarlos y extraer su texto
    for file in files:
        filename = secure_filename(file.filename)  # Asegurar el nombre del archivo
        print(filename)  # Imprimir el nombre del archivo para depuración
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Crear la ruta del archivo
        file.save(file_path)  # Guardar el archivo en la carpeta de carga
        consolidated_text += extract_text_from_file(file_path) + "\n"  # Agregar el texto extraído

    # Eliminar caracteres no deseados del texto consolidado
    consolidated_text = re.sub(r"[´˜¸]", "", consolidated_text)
    
    # Escribir el texto consolidado en un archivo (input.txt)
    with open('input.txt', 'w', encoding='utf-8') as f:
        f.write(consolidated_text)

    print(os.getcwd())  # Imprimir el directorio de trabajo actual para depuración
    # Ejecutar comandos externos (por ejemplo, 'make' y un parser) sobre el texto de entrada
    os.system('make')  # Ejecutar el comando make para construir
    os.system('./parser input.txt output.txt')  # Ejecutar el parser sobre el archivo de entrada

    # Leer los resultados del archivo de salida
    with open('output.txt', 'r', encoding='utf-8') as f:
        results = f.read()

    # Parsear el texto de los resultados y devolverlo en formato JSON
    return parse_text_to_json(results)

# Función para parsear el texto extraído en un formato JSON estructurado
def parse_text_to_json(text):
    # Inicializar el diccionario para almacenar los resultados
    result = {
        "emails": [],
        "urls": [],
        "references": []
    }
    
    # Expresiones regulares para capturar emails, urls y referencias
    email_pattern = r"EMAIL: ([\w\.-]+@[\w\.-]+\.\w+)"
    url_pattern = r"URL: (https?://[^\s]+)"
    reference_pattern = r"NAME: ([^:]+?) TITLE: \((\d{4})\)\. ([^\n]+)"
    
    # Buscar y añadir emails
    emails = re.findall(email_pattern, text)
    result["emails"].extend(emails)
    
    # Buscar y añadir URLs
    urls = re.findall(url_pattern, text)
    result["urls"].extend(urls)
    
    # Buscar y añadir referencias
    references = re.findall(reference_pattern, text)
    for reference in references:
        authors = [name.strip() for name in reference[0].split("NAME:")]
        title = reference[2].strip()
        year = reference[1]
        result["references"].append({
            "authors": authors,
            "year": year,
            "title": title
        })
    
    # Devolver los resultados como JSON
    return json.dumps(result, indent=4, ensure_ascii=False)
    
# Ejecutar la aplicación Flask si este archivo es el principal
if __name__ == '__main__':
    app.run(debug=True)
