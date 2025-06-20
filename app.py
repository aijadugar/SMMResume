from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import base64
from io import BytesIO
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GEMINI_API)

app = Flask(__name__)
CORS(app)

def extract_text_from_pdf_bytes(pdf_bytes):
    reader = PdfReader(BytesIO(pdf_bytes))
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_resume_details(text):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = f"""
    Extract the candidate's full name and key skills from this resume text, and write a 2-3 line summary of their strengths:

    Resume:
    {text}

    Format:
    Name: <full name>
    Skills: <comma separated skills>
    Summary: <short summary>
    """
    response = model.generate_content(prompt)
    return response.text

@app.route("/", methods=["POST"])
def upload_resume():
    try:
        data = request.get_json()
        base64_file = data.get("base64")

        if not base64_file:
            return jsonify({"message": "No file content received."}), 400

        file_bytes = base64.b64decode(base64_file)
        text = extract_text_from_pdf_bytes(file_bytes)
        result = extract_resume_details(text)

        return jsonify({"message": result})

    except Exception as e:
        return jsonify({"message": f"Error processing file: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
