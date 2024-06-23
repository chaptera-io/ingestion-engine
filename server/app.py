from flask import Flask, request, jsonify
import firebase_admin
import uuid
from firebase_admin import credentials, firestore
import os



# infer credentials from environment variables
firebase_admin.initialize_app()

# OpenAI API Configuration
openai.api_key = os.environ.get('OPENAI_API_KEY')


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

        # Generate random hash for document ID
        doc_id = str(uuid.uuid4())

        # Create document reference in the raw collection
        doc_ref = db.collection('raw').document(doc_id)

        # Set document data
        doc_ref.set({
            "tag": f"{project_name}/{chapter}/{type}",
            "content": content
        })

        return jsonify({"message": "Content for {project_name}/{chapter}/{type} stored successfully"}), 200
    
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
    