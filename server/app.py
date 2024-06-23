from flask import Flask, request, jsonify
import firebase_admin
import uuid
from firebase_admin import credentials, firestore
import os
import openai
from openai import OpenAI
import pdfplumber
import openai
import io
import json
import datetime
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

        # OpenAI API call
        key = os.environ.get('OPENAI_API_KEY')

        client = OpenAI(
            # This is the default and can be omitted
            # api_key=os.getenv("OPENAI_API_KEY"),
            api_key=key
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": """You are a friendly, yet highly professional tutor. You are very confident of your answers given your information source. Read the chapter, and give me a combination of 
                    script for narration and content for the slide. Each slide will have a title and some bullet points. 
                    Chapter= """ + extracted_text + """.
                    As an experienced tutor, you give detailed bullet points that briefly summarize each 
                    concept, not just list them as a title. Further, you. are very meticulous, and make lots of bullet points for each main topic, not just a few. The bullet points should look like 'concept name - 
                    few words ultra brief summary'  
                    Make sure to give me only the json output in the following schema:[ { slideTitle: string, bulletPoints: [ { bulletPoint: string, narration: string } ] } ]. Absolutely no extra text or formatting."""
                }   
            ],
            model="gpt-4o",
        )

        # print(chat_completion.choices[0].message.content) 


        script_data = json.loads(chat_completion.choices[0].message.content)

        try:
            # Store TextDump in Firestore
            doc_id = str(uuid.uuid4())
            doc_ref = db.collection('raw').document(doc_id)
            doc_ref.set({
                "content": extracted_text, 
                "tag": f"{project_name}/{chapter}/raw",
            })
            
            # Store script data in Firestore
            doc_id = str(uuid.uuid4())
            script_id = doc_id
            doc_ref = db.collection('scripts').document(doc_id)
            doc_ref.set({
                "sections": script_data, 
                "tag": f"{project_name}/{chapter}/script",
            })
            
            # Store Job in Firestore
            doc_id = str(uuid.uuid4())
            doc_ref = db.collection('jobs').document(doc_id)
            doc_ref.set({
                "created_at": datetime.datetime.now(),
                "script_id": script_id,
                "status": "queued"
            })

            return jsonify({"message": f"Content for {project_name}/{chapter}/{content_type} stored successfully, job successfully created."}), 200
        

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    
@app.route('/get_narration', methods=['GET'])
def get_narration(): 
    tag = request.args.get('tag')
        
    if not tag:
        return jsonify({"error": "Missing 'tag' parameter"}), 400
        
    try:
        # Query documents with the matching tag
        docs = db.collection('scripts').where('tag', '==', tag).stream()

        all_narration = ""

        for doc in docs:
            script_data = doc.to_dict()['sections']
            for section in script_data:
                for bullet_point in section['bulletPoints']:
                    all_narration += bullet_point['narration'] + " "

        key = os.environ.get('OPENAI_API_KEY')
        client = OpenAI(
            api_key=key
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": """You are a friendly, yet highly professional tutor. Based on the data_input """ + all_narration + """,
                    construct three thought provoking free response questions that require one to two sentence long responses. Output
                    as a list of three strings. Return nothing else. Format should be [Question_String1, Question_String2, Question_String3 ]"""
                }   
            ],
            model="gpt-4o",
        )
        
        # transform chat_completion to list of strings
        
        try:
            question_list = json.loads(chat_completion.choices[0].message.content)
            doc_id = str(uuid.uuid4())
            doc_ref = db.collection('short_response').document(doc_id)
            doc_ref.set({
                "questions": question_list,
            })

            return jsonify({"message": "Questions stored successfully, job successfully created."}), 200
        

        except Exception as e:
            return jsonify({"error": str(e)}), 500 
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            question_list = []


        # get user input
        
            
        # pass rubric and user input to gpt to grade and give feed back
        # store question, user_input,feedback

        # store question, rubric (generated)
        try:
            
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/check_FRQ_answer', methods=['GET'])
def check_FRQ_answer():
   

if __name__ == '__main__':
    app.run(debug=True)
    