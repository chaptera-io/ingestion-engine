from flask import Flask, request, jsonify
import firebase_admin
import uuid
from firebase_admin import credentials, firestore
import os
import openai
import pdfplumber
import openai
import io



import requests
 
# infer credentials from environment variables
firebase_admin.initialize_app()
 
# OpenAI API Configuration
openai.api_key = os.environ.get('OPENAI_API_KEY')
 
 
app = Flask(__name__)
db = firestore.client()
 
# def load_extracted_data(file_path):
#     """
#     Loads extracted data from a JSON file.
#     """
#     with open(file_path, 'r') as f:
#         return json.load(f)
 
@app.route('/store_content', methods=['POST'])
def store_content():
 
# Define PDF file path and other details directly
# pdf_path = "/Users/jq4386/Github/Personal/berkeley-hackathon/Chapter 9.pdf"  # Replace with your actual path
    data = request.get_json()
    project_name = data['project_name']
    chapter = data['chapter']
    content_type = data['content_type']
    url = data['url']

    def extract_text_from_page(page):
        """
        Extracts text from a single PDF page, attempting OCR if the initial extraction fails.
        """
        text = page.extract_text(x_tolerance=3, y_tolerance=3)
        if not text:
            text = page.extract_text(x_tolerance=3, y_tolerance=3, use_text_flow=True, extra_attrs=["fontname", "size"])
        return text

    def get_pdf_bytes(url):
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.content

    def extract_text_from_pdf(pdf_url):
        pdf_bytes = get_pdf_bytes(pdf_url)
        extracted_text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}...")
                extracted_text += extract_text_from_page(page) + "\n\n"
        return extracted_text

    try:
        # Extract text directly from PDF
        extracted_text = extract_text_from_pdf(url)

        # Generate document ID and store in Firestore
        doc_id = str(uuid.uuid4())
        doc_ref = db.collection('raw').document(doc_id)
        doc_ref.set({
            "tag": f"{project_name}/{chapter}/{content_type}",
            "content": extracted_text  
        })

        return jsonify({"message": f"Content for {project_name}/{chapter}/{content_type} stored successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    
@app.route('/get_content', methods=['GET'])
def get_content():
    try: 
        tag = request.args.get('tag')
        
        if not tag:
            return jsonify({"error": "Missing 'tag' parameter"}), 400
        
        # Query documents with the matching tag
        docs = db.collection('raw').where('tag', '==', tag).limit(1).get()
        doc = docs[0]

        if not doc:
            return jsonify({"message": "there is no raw content associated with {tag} in the database"}), 404

        fetched_content = doc.get('content')

        # OpenAI API call
        response = openai.Completion.create(
            model="gpt-4o",
            prompt=f""
        )

        return jsonify({"content": fetched_content}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
    