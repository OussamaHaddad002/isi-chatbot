import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import pdfplumber
import PyPDF2
from dotenv import load_dotenv
import json
from unidecode import unidecode

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))

# Define the index name and dimension
index_name = "isidb"
dimension = 384  # Dimension for all-MiniLM-L6-v2 embeddings

# Check if the index exists, create it if not
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

# Access the index
index = pc.Index(index_name)

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to process a single PDF file using pdfplumber and fallback to PyPDF2
def process_pdf(file_path):
    text = ""
    
    # First try using pdfplumber
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text
            else:
                print(f"Warning: No text extracted from page {page_num + 1} using pdfplumber, trying PyPDF2.")
                text += extract_text_with_pypdf2(file_path)
                
    # If no text is found with pdfplumber, try PyPDF2
    if not text:
        print(f"Attempting to extract text using PyPDF2 for file: {file_path}")
        text = extract_text_with_pypdf2(file_path)
    
    return text

# Function to extract text from PDF using PyPDF2
def extract_text_with_pypdf2(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text
            else:
                print(f"Warning: No text extracted from page {page_num + 1} using PyPDF2.")
    return text

# Function to sanitize the vector ID (convert to ASCII)
# Function to sanitize the vector ID (convert to ASCII)
# Function to sanitize the vector ID (convert to ASCII)
def sanitize_filename(file_name):
    # Use unidecode to convert any non-ASCII characters to ASCII equivalents
    sanitized_name = unidecode(file_name)
    # Optionally, replace spaces with underscores for better formatting in vector IDs
    sanitized_name = sanitized_name.replace(" ", "_")

    # Ensure that the sanitized name only contains ASCII characters
    if not all(ord(c) < 128 for c in sanitized_name):
        raise ValueError(f"Vector ID must be ASCII, but got: {sanitized_name}")

    return sanitized_name  # Return the sanitized, ASCII-only string



# Function to split text into smaller chunks
def split_text(text, max_length=300):
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Function to check metadata size and trim if necessary
def check_metadata_size(metadata, max_size=40960):
    # Convert metadata to JSON string and check its size
    metadata_json = json.dumps(metadata)
    metadata_size = len(metadata_json.encode('utf-8'))
    
    # If metadata exceeds the size limit, trim the content
    if metadata_size > max_size:
        print(f"Warning: Metadata size {metadata_size} bytes exceeds limit. Truncating content.")
        metadata['content'] = metadata['content'][:max_size // 2]  # Truncate content to fit within the limit
        metadata_json = json.dumps(metadata)  # Recalculate the size
        metadata_size = len(metadata_json.encode('utf-8'))
        # Further truncate if necessary
        if metadata_size > max_size:
            metadata['content'] = metadata['content'][:max_size // 4]  # Further truncate if still over the limit
    return metadata

# Function to load and upsert a single PDF
def load_and_upsert_single_pdf(file_path, namespace):
    text = process_pdf(file_path)

    # Check if the text was extracted
    if not text:
        print(f"Failed to extract text from {file_path}")
        return

    # Sanitize file name for metadata
    sanitized_file_name = sanitize_filename(os.path.basename(file_path))

    # Split text into chunks for more relevant querying
    chunks = split_text(text)
    documents = []
    for i, chunk in enumerate(chunks):
        embeddings = model.encode([chunk])[0]
        
        # Prepare metadata
        metadata = {
            "file_name": sanitized_file_name,
            "chunk_number": i,
            "content": chunk  # Add the actual content here
        }
        
        # Check and trim metadata if it exceeds the size limit
        metadata = check_metadata_size(metadata)

        # Create the document with metadata
        documents.append({
            "id": f"{namespace}_{sanitized_file_name}_chunk_{i}",  # Ensure vector ID is ASCII
            "values": embeddings,
            "metadata": metadata
        })

    # Upsert documents into Pinecone index
    index.upsert(vectors=documents)
    print(f"Successfully upserted {len(documents)} chunks from '{sanitized_file_name}' under namespace '{namespace}'.")

# Function to process all PDFs in a folder and its subfolders
def process_folder(folder_path):
    # Walk through all files and subfolders in the given folder
    for root, dirs, files in os.walk(folder_path):
        # The namespace will be the current folder name (without the full path)
        namespace = os.path.basename(root)
        for file in files:
            if file.lower().endswith('.pdf'):  # Process only PDF files
                file_path = os.path.join(root, file)
                load_and_upsert_single_pdf(file_path, namespace)

# Specify the folder containing your PDFs
folder_path = "C:/Users/MSI/Desktop/dataaa/Dossier_Accreditation CTI_ISI_2024__"  # Update with your folder path
process_folder(folder_path)

# Example query to test the embeddings
query_vector = model.encode(["What is the summary of the document?"])[0].tolist()  # Convert the vector to a list

response = index.query(
    vector=query_vector,
    top_k=2,  # Retrieve the top 2 most similar documents
    include_values=True,
    include_metadata=True
)

# Print the response with content
for match in response['matches']:
    print(f"Namespace: {match['metadata']['file_name']}")
    print(f"Content: {match['metadata']['content'][:500]}...")  # Display the first 500 chars of content
