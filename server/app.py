from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os


app = Flask(__name__)
db = firestore.client()

@app.route('/store_content', methods=['POST'])
def store_content():
    try:
        data = request.get_json()

        project_name = data['project_name']
        chapter = data['chapter']
        type = data['type']
        content = data['content']

        # Create Firestore document ID
        doc_id = f"{project_name}/{chapter}/{type}"

        # Create document reference
        doc_ref = db.collection('content').document(doc_id)

        # Set document data
        doc_ref.set({
            "content": content
        })

        return jsonify({"message": "Content for {project_name}/{chapter}/{type} stored successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
    