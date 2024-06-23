from flask import Flask, request, jsonify
import firebase_admin
import uuid
from firebase_admin import credentials, firestore
import os
import json

# infer credentials from environment variables
firebase_admin.initialize_app()


app = Flask(__name__)
db = firestore.client()

def load_extracted_data(file_path):
    """
    Loads extracted data from a JSON file.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

@app.route('/store_content', methods=['POST'])
def store_content():
    try:
        data = request.get_json()
        file_path = data['file_path']  # Get the path to your JSON file

        # Load extracted data from JSON
        extracted_data = load_extracted_data(file_path)

        # Extract specific fields from the JSON data
        project_name = extracted_data['project_name']
        chapter = extracted_data['chapter']
        type = extracted_data['type']  # Note: using 'type' instead of the reserved keyword 'type'
        content = extracted_data['content']
        
        # Generate document ID and store
        doc_id = str(uuid.uuid4())
        doc_ref = db.collection('raw').document(doc_id)
        
        # Set document data using extracted values
        doc_ref.set({
            "tag": f"{project_name}/{chapter}/{type}",
            "content": content
        })

        return jsonify({"message": f"Content for {project_name}/{chapter}/{type} stored successfully"}), 200

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

        return jsonify({"content": fetched_content}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
    