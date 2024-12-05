# <img src="https://github.com/user-attachments/assets/97437d6a-821e-49d1-a92e-6c498467cd9f" width="120" valign="middle" alt="Scapy" />&nbsp;


AutoApplyAI is an intelligent job application assistant designed to streamline and automate the application process across various platforms. By leveraging advanced Large Language Models (LLMs), it ensures accurate, context-aware form filling while eliminating the need for costly subscriptions. With just one click, AutoApplyAI extracts information directly from the user's resume and seamlessly completes online job applications, providing a hassle-free experience.

## Project Aim

The aim of AutoApplyAI is to streamline the job application process by:
- Efficiently extracting and processing user data from resumes and profiles.
- Intelligently inferring and filling in missing information using advanced AI.
- Providing a seamless, fully automated application submission experience.
- Generating tailored drafts for various application requirements based on the user's profile.
- Automatically responding to new questions or fields in applications using an LLM-powered pipeline, ensuring accurate and precise form filling.

The tool offers a smarter, subscription-free alternative to existing autofill services, ensuring compatibility and precision even with complex form structures.

## Directory Structure
```
AutoApplyAI/
├── backend_server/
│   ├── app.py
│   ├── utils.py
│   ├── .env
│   ├── user_data/
│   │   ├── user_resume.pdf
│   │   ├── user_transcript.pdf
│   │   ├── user_data.json
│   │   └── file.json
├── chrome_extension/
│   ├── background.js
│   ├── contentScript.js
│   ├── manifest.json
│   ├── popup.js
│   ├── popup.html
│   └── icons/
│       └── icon128.png
│       └── ...
├── readme.md
└── requirement.txt
```

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/AutoApplyAI.git
    cd AutoApplyAI
    pip install -r requirement.txt
    ```

2. Set up the backend server:
    ```sh
    cd backend_server
    ```

3. Set up environment variables:
    Create a `.env` file in the `backend_server` directory and add your OpenAI API key:
    ```env
    OPENAI_API_KEY_1=your_openai_api_key
    ```

## Usage

1. **Run the Backend Server:**
    ```sh
    cd backend_server
    python app.py
    ```

2. **Use the Chrome Extension:**
    To load the extension in Chrome:
   - Open Chrome and navigate to `chrome://extensions/`.
   - Enable "Developer mode" by toggling the switch in the top right corner.
   - Click on "Load unpacked" and select the `chrome_extension` directory from the project folder.
    
## How It Works

1. **Data Extraction:**
   - The backend server extracts essential information from user resumes and other uploaded documents.
   - The LLM identifies additional required details and prompts the user to provide them, ensuring all necessary information is gathered.
   - Extracted data is stored in a structured file (`user_data.json`) for efficient reuse by the system during form completion.

2. **Form Filling:**
   - The Chrome extension interacts directly with job application forms on web pages.
   - It extracts the form fields and sends them to the backend server for processing.
   - The backend server forwards the fields to the LLM, which generates contextually accurate responses for each field based on the stored user data.
   - The responses are then sent back to the Chrome extension, which automatically fills out the forms, ensuring a smooth and precise application process.

An overview of the workflow is shown below:

<p align="center">
  <img src="https://github.com/user-attachments/assets/1d82a09a-d863-40b3-aca3-678c9bd33d14" width="700" height="300">
</p>

## Contributing

The Project will be expanded further and contributions are welcome! Please fork the repository and submit a pull request.


