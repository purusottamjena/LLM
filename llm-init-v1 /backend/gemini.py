import os
import tempfile
import requests
from git import Repo

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-002:generateContent"

def clone_and_extract_code(github_url):
    """Clone the GitHub repo and extract C/C++ files."""
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
        
        # Combine all files into a single string (you can adjust this logic)
        combined_code = "\n\n".join(code_files)
        return combined_code
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

def generate_test_cases_gemini_from_github(github_url, api_key):
    """Generate test cases for a GitHub repository using Gemini."""
    # Clone and extract code
    code = clone_and_extract_code(github_url)
    if code.startswith("Error"):
        return code
    
    # Prepare API payload
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"Generate unit test cases for the following C++ code:\n{code}\n for using cpputest framework, with proper syntaxing, including main, with proper c cpp naming conventions with respect to MISHRA C guidelines"}
                ]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_API_URL}?key={api_key}"

    # Send API request
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Error: {response.status_code} - {response.text}"


def generate_test_cases_gemini(code, api_key):
    """Generate test cases using Gemini."""
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"Generate unit test cases for the following C++ code:\n`c++\n{code}\n`"}
                ]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_API_URL}?key={api_key}"

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Error: {response.status_code} - {response.text}"