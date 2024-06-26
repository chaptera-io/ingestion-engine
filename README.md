# InfoWeaver - Information Ingestion Module

This module serves as the backbone of the InfoWeaver platform, enabling the seamless ingestion and processing of educational content from various sources, including PDFs, lecture transcripts, and more. It utilizes a robust tech stack, including Firebase for data storage, Flask for web service, OpenAI GPT-4o for content summarization and question generation, and pdfplumber for PDF text extraction.

## Key Features

* **Diverse Content Ingestion:** Supports PDF ingestion with robust text extraction, including OCR capabilities.
* **Intelligent Content Processing:** Employs OpenAI GPT-4o for accurate summarization, slide generation, and question formulation.
* **Structured Data Storage:** Stores extracted content, generated slides, and questions in a Firebase database for easy access and retrieval.
* **Scalable Web Service:** Built on Flask, ensuring efficient handling of incoming content and API requests.

## Technical Implementation

1. **Content Upload (POST /store_content):**
   - Receives raw educational content (e.g., PDF URLs).
   - Extracts text from PDFs using pdfplumber, including OCR when necessary.
   - Sends extracted text to OpenAI GPT-4o for summarization and slide generation.
   - Stores raw text, generated slides, and questions in Firebase.

2. **Narration and Question Generation (GET /get_narration):**
   - Retrieves relevant content based on the provided tag.
   - Utilizes OpenAI GPT-4o to generate engaging narration scripts and thought-provoking questions.
   - Stores generated narration scripts and questions in Firebase.

## Future Enhancements

* **Expanded Content Sources:** Support for additional content formats like videos, images, and web pages.
* **Enhanced Content Processing:** Integration of more sophisticated NLP techniques for deeper content analysis and personalized learning experiences.
* **Real-time Feedback:** Development of a feedback loop for continuous improvement of content quality and relevance.

## Installation and Setup

1. Clone the repository:

```bash
git clone https://your_repo_url
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up Firebase:

   - Create a Firebase project.
   - Obtain your Firebase credentials (service account key).
   - Set the following environment variables:
     - `OPENAI_API_KEY`: Your OpenAI API key.
     - `FIREBASE_CREDENTIALS`: Path to your Firebase credentials file.

4. Run the Flask app:

```bash
flask run
```


## License

This project is licensed under the [MIT License](link_to_license_file).
