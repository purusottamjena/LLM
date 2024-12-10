import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile

# Import your existing test case generation functions
from llama import generate_test_cases_llama_from_text, generate_test_cases_llama_from_github
from gemini import generate_test_cases_gemini, generate_test_cases_gemini_from_github

app = Flask(__name__)
CORS(app)

@app.route('/generate-test-cases', methods=['POST'])
def generate_test_cases():
    """
    Flask route to handle file uploads and GitHub URL test case generation
    """
    try:
        # Determine input type
        if request.is_json:
            # GitHub URL input
            data = request.json
            github_url = data.get('github_url')
            model = data.get('model', 'llama')
            api_key = data.get('api_key', '')

            if not github_url:
                return jsonify({'error': 'GitHub URL is required'}), 400

            # Generate test cases from GitHub URL
            if model == 'llama':
                test_cases = generate_test_cases_llama_from_github(github_url)
            elif model == 'gemini':
                test_cases = generate_test_cases_gemini_from_github(github_url, api_key)
            else:
                return jsonify({'error': 'Invalid model selected'}), 400

            return jsonify({'test_cases': test_cases})
        
        # File upload input
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400

        # Get files and model details
        files = request.files.getlist('files')
        model = request.form.get('model', 'llama')
        api_key = request.form.get('api_key', '')

        # Validate files
        if not files:
            return jsonify({'error': 'No files selected'}), 400

        # Create a temporary directory to store uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            file_paths = []
            for file in files:
                if file.filename.endswith(('.c', '.h')):
                    filepath = os.path.join(temp_dir, file.filename)
                    file.save(filepath)
                    file_paths.append(filepath)

            # Read file contents
            file_contents = []
            for filepath in file_paths:
                with open(filepath, 'r') as f:
                    file_contents.append(f.read())

            # Combine file contents
            combined_code = '\n'.join(file_contents)

            # Generate test cases based on selected model
            if model == 'llama':
                test_cases = generate_test_cases_llama_from_text(combined_code)
            elif model == 'gemini':
                test_cases = generate_test_cases_gemini(combined_code, api_key)
            else:
                return jsonify({'error': 'Invalid model selected'}), 400

            return jsonify({'test_cases': test_cases})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)