import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from together import Together
import numpy as np
import speech_recognition as sr
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tempfile
from langdetect import detect, LangDetectException

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
index_name = "isidb"
index = pc.Index(index_name)

# Initialize Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Together API client
client = Together(api_key=os.getenv("TOGETHER_AI_API_KEY"))

# Function to query Pinecone
def query_pinecone(query, top_k=3):
    try:
        query_vector = model.encode([query])[0]
        query_vector = query_vector.tolist()

        response = index.query(
            vector=query_vector,
            top_k=top_k,
            include_values=False,
            include_metadata=True
        )

        if 'matches' in response:
            documents = []
            for item in response['matches']:
                file_name = item['metadata'].get('file_name', 'No file name')
                content = item['metadata'].get('content', 'No content available')
                documents.append(f"File: {file_name}\nContent: {content[:500]}")
            return "\n".join(documents)
        else:
            return "No matches found."
    except Exception as e:
        return f"Error querying Pinecone: {str(e)}"

# Function to generate response from model
# Function to generate response from model
def generate_with_model(query, context, image_url=None):
    try:
        language = detect(query) if query else "en"

        if language == 'fr':
            chatbot_role = """
            Vous êtes un assistant universitaire à l'ISI (Institut Supérieur d'Informatique), une université prestigieuse.
            Répondez aux questions des étudiants et des visiteurs sur les programmes, les admissions et les ressources de manière concise et directe.
            Évitez les réponses longues et concentrez-vous sur les informations essentielles.
            """
        else:
            chatbot_role = """
            You are a university assistant at the ISI (Institut Supérieur d'Informatique), a prestigious university.
            Answer students' and visitors' questions about programs, admissions, and resources in a concise and straightforward manner.
            Avoid lengthy responses and focus on essential information.
            """

        # Prepare input with only valid fields
        input_data = [{"role": "system", "content": chatbot_role}]
        
        # Add text and image URL separately in the required format
        if query:
            input_data.append({
                "role": "user",
                "content": query
            })
        if image_url:
            input_data.append({
                "role": "user",
                "content": image_url
            })

        # Send the query and image to the model
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=input_data
        )

        # Extract and return the response content
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "Error: No valid choices found in the response."
    except Exception as e:
        return f"Error generating response: {str(e)}"


# RAG System (Retrieve and Generate)
def rag_system(query, image_url=None):
    documents = query_pinecone(query) if query else ""

    if documents == "No matches found.":
        return generate_with_model(query, "I'm sorry, I couldn't find any relevant information in my knowledge base.", image_url)

    prompt = f"Here is some context:\n{documents}\n\nAnswer the following question: {query}"
    response = generate_with_model(query, prompt, image_url)

    return response

# Root route to render the HTML interface
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Chatbot response route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query")
    image_url = data.get("image_url")
    
    response = rag_system(query, image_url)
    return jsonify({"response": response})

# Speech recognition route
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio_file:
        file.save(temp_audio_file.name)
        with sr.AudioFile(temp_audio_file.name) as source:
            audio = recognizer.record(source)
            try:
                transcription = recognizer.recognize_google(audio)
                return jsonify({"transcription": transcription})
            except sr.UnknownValueError:
                return jsonify({"error": "Audio not clear, please try again."}), 400
            except sr.RequestError:
                return jsonify({"error": "Could not request results; check your network connection."}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
