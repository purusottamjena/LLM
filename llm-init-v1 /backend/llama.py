import os
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv
import tempfile
from git import Repo

# Load environment variables
load_dotenv()

# Initialize embedding model globally with a valid HuggingFace model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

def initialize_llama_llm():
    """
    Initialize the Ollama LLM locally.
    """
    return Ollama(
        model="llama3.2",
        request_timeout=300.0,
        max_tokens=4000, 
    )

def process_query_response(response):
    """
    Extract and return the text content from a query response.
    """
    try:
        # Convert response to string or text, stripping unnecessary structures
        if hasattr(response, "response"):
            return response.response.strip()
        elif isinstance(response, str):
            return response.strip()
        else:
            return str(response).strip()
    except Exception as e:
        return f"Error processing response: {str(e)}"

def generate_test_cases_llama_from_text(code):
    """
    Generate test cases for given C/C++ code using LlamaIndex with Ollama.
    """
    try:
        # Initialize LLM
        llm = initialize_llama_llm()
        Settings.llm = llm

        # Create a document from the provided code
        document = Document(text=code)

        # Create an index with the embedding model
        index = VectorStoreIndex.from_documents([document])

        # Set up the query engine (non-streaming for simplicity)
        query_engine = index.as_query_engine(llm=llm, similarity_top_k=1)

        # Query the index
        query = "Generate unit test cases for the provided C and C++ code."
        response = query_engine.query(query)

        # Extract and return the response text
        # return process_query_response(response)
        # Safely extract the response text
        if hasattr(response, 'response'):
            return response.response
        elif hasattr(response, 'text'):
            return response.text
        else:
            return str(response)
    except Exception as e:
        return f"Error: {str(e)}"


def clone_and_extract_code(github_url):
    """
    Clone the GitHub repository and extract C/C++ files.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        # Clone the repository
        Repo.clone_from(github_url, temp_dir)
        
        # Collect all C/C++ files
        code_files = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(('.c', '.cpp', '.h', '.hpp')):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        code_files.append(f.read())
        
        # Combine all files into a single string
        if not code_files:
            return "Error: No C/C++ files found in the repository."
        return "\n\n".join(code_files)
    except Exception as e:
        return f"Error cloning or processing repository: {str(e)}"
    finally:
        # Cleanup temporary directory
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_dir)
        except Exception:
            pass

def generate_test_cases_llama_from_github(github_url):
    """
    Generate test cases for C/C++ files in a GitHub repository using LlamaIndex locally.
    """
    try:
        # Clone and extract code from the repository
        code = clone_and_extract_code(github_url)
        if code.startswith("Error"):
            return code
        
        # Initialize LLM
        llm = initialize_llama_llm()
        Settings.llm = llm

        # Create a document from the extracted code
        document = Document(text=code)

        # Create an index with the embedding model
        index = VectorStoreIndex.from_documents([document])

        # Set up the query engine
        query_engine = index.as_query_engine(llm=llm, similarity_top_k=4)

        # Query the index
        query = "Generate unit test cases for the following C and C++ code."
        response = query_engine.query(query)

        # Extract and return the response text
        # return response.response if hasattr(response, "response") else str(response)
        # Safely extract the response text
        if hasattr(response, 'response'):
            return response.response
        elif hasattr(response, 'text'):
            return response.text
        else:
            return str(response)
    except Exception as e:
        return f"Error: {str(e)}"