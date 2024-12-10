document.addEventListener('DOMContentLoaded', () => {
    const inputTypeRadios = document.querySelectorAll('input[name="input-type"]');
    const fileUploadContainer = document.getElementById('file-upload-container');
    const githubUploadContainer = document.getElementById('github-upload-container');
    const fileUpload = document.getElementById('file-upload');
    const githubUrlInput = document.getElementById('github-url');
    const fileList = document.getElementById('file-list');
    const generateBtn = document.getElementById('generate-btn');
    const modelSelect = document.getElementById('model-select');
    const errorMessage = document.getElementById('error-message');
    const testCasesElement = document.getElementById('test-cases');

    // Default API keys (replace with actual values)
    const llamaApiKey = "";
    const geminiApiKey = "";

    // Track uploaded files
    let uploadedFiles = [];

    // Input type toggle
    inputTypeRadios.forEach(radio => {
        radio.addEventListener('change', (event) => {
            if (event.target.value === 'file') {
                fileUploadContainer.style.display = 'block';
                githubUploadContainer.style.display = 'none';
                validateInputs();
            } else {
                fileUploadContainer.style.display = 'none';
                githubUploadContainer.style.display = 'block';
                validateInputs();
            }
        });
    });

    // File upload event listener
    fileUpload.addEventListener('change', (event) => {
        uploadedFiles = Array.from(event.target.files)
            .filter(file => file.name.endsWith('.c') || file.name.endsWith('.h'));

        // Update file list display
        fileList.innerHTML = uploadedFiles.map(file => 
            `<div>${file.name}</div>`
        ).join('');

        validateInputs();
    });

    // GitHub URL input listener
    githubUrlInput.addEventListener('input', validateInputs);

    // Validate inputs and enable/disable generate button
    function validateInputs() {
        const selectedInputType = document.querySelector('input[name="input-type"]:checked').value;
        
        if (selectedInputType === 'file') {
            generateBtn.disabled = uploadedFiles.length === 0;
        } else {
            generateBtn.disabled = !githubUrlInput.value.trim();
        }
    }

    // Generate test cases
    generateBtn.addEventListener('click', async () => {
        // Reset previous state
        errorMessage.textContent = '';
        testCasesElement.textContent = '';
        generateBtn.disabled = true;

        const selectedInputType = document.querySelector('input[name="input-type"]:checked').value;

        try {
            let response;
            if (selectedInputType === 'file') {
                // File upload flow
                const formData = new FormData();
                uploadedFiles.forEach(file => {
                    formData.append('files', file);
                });
                
                formData.append('model', modelSelect.value);
                formData.append('api_key', 
                    modelSelect.value === 'llama' ? llamaApiKey : geminiApiKey
                );

                response = await fetch('http://0.0.0.0:5000/generate-test-cases', {
                    method: 'POST',
                    body: formData
                });
            } else {
                // GitHub URL flow
                response = await fetch('http://0.0.0.0:5000/generate-test-cases', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        github_url: githubUrlInput.value,
                        model: modelSelect.value,
                        api_key: modelSelect.value === 'llama' ? llamaApiKey : geminiApiKey
                    })
                });
            }

            if (response.ok) {
                const data = await response.json();
                testCasesElement.textContent = data.test_cases;
            } else {
                const error = await response.text();
                errorMessage.textContent = `Error: ${error}`;
            }
        } catch (error) {
            errorMessage.textContent = `Error: ${error.message}`;
        } finally {
            generateBtn.disabled = false;
        }
    });
});