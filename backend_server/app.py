import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import json
import re
from jsonschema import validate, ValidationError
from utils import check_resume_and_transcript,check_user_data_json,print_in_box
 

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_1', '')
resume_path = None
transcript_path = None

def setup_paths():
    global resume_path, transcript_path
    resume_path, transcript_path = check_resume_and_transcript()

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize LangChain and OpenAI
llm = ChatOpenAI(model="gpt-4o",api_key= OPENAI_API_KEY, temperature=0.2)  # Replace with your OpenAI API key

setup_paths()
check_user_data_json(resume_path)

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["form_fields", "user_data"],
    template="""
You are an intelligent assistant tasked with filling out a job application form based on the user's provided information. Below are the form fields and the user's data. Please intelligently process all fields and provide the output in the specified JSON format. 

**Form Fields:**
{form_fields}

**User Data:**
{user_data}

**Instructions:**
1. For each form field, determine the appropriate value using the user data.
2. Make sure to provide answer for all the form_fields, and if there is large text required provide that too. For example, if there is cover letter require in the text field (Comment) provide the cover letter content.
2. **Handling Field Types:**
   - **Checkbox (`type: checkbox`)**: Set `value` to `"true"` if it should be true as per the user data or common practice, otherwise `"false"`. For Checkbox where you have to select one option, always provide one option `"true"` or all. For example, question asking about when you are available to start, provide atleast one checkbox `"true"`.
   - **Radio (`type: radio`)**: For type radio, Only set `value` to `"true"` or `"false"` based on the information you have about the user and normal practice. Do not answer anything else than true or false. Moreover, Expected output should always contain the same number of radio type entries as there were in form fields even though if they are duplicated.
   - **Select-One (`type: select-one`)**: Choose the appropriate option that suits best for this type of selection in the job application forms based on the user's data. Make sure to always proivde answer to each `type: select-one` from the options available in the label.
   - **Detail Text (`type: textarea`)**: Analyze and see if there is cover letter text required, if so provide a brief cover letter using the user's data.
   - **Text, Email, etc.**: Use the user's provided input as the `value`.
   - **Button (`type button`)**: For the type button, set the `value` to `"true"` if it is submit button. You can analyze through its label.
3. **Formatting:**
   - Output the data as a JSON array of objects.
   - Do not include any special character in your responses.
   - Each object should have:
     - `"name"`: The field's `name` attribute.
     - `"value"`: The processed value as per the above instructions.
   - Do not include any additional text or explanations.

**Example:**

**Form Fields:**
[
    {{"name": "emailAgreement", "label": "Email Agreement", "type": "checkbox"}},
    {{"name": "cntryFields.firstName", "label": "First Name*", "type": "text"}},
    {{"name": "candidateSelfIdentifyAsPriorWorker.true", "label": "Yes", "type": "radio"}},
    {{"name": "gender", "label": "Female", "type": "radio"}}
    {{'name': 'submit_app', 'label': 'Submit Application', 'type': 'button'}}
    
]


**User Data:**
{{
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "123-456-7890",
    "address": "123 Main St, Apt 808",
    "city": "Bryan",
    "state": "Texas",
  }}

**Expected Output:**
[
    {{"name": "emailAgreement", "value": "true"}},
    {{"name": "cntryFields.firstName", "value": "Jane"}},
    {{"name": "candidateSelfIdentifyAsPriorWorker.true", "value": "false"}},
    {{"name": "gender", "value": "false"}}
    {{'name': 'submit_app', 'value': 'true'}}
]

**Now, process the Form Fields and User Data.**

Response:
"""
)

llm_chain = prompt_template | llm

# Load user data from a JSON file
with open('user_data/user_data.json', 'r') as f:
    user_data = json.load(f)

@app.route('/fill-form', methods=['POST'])
def fill_form():
    data = request.json
    form_fields = data.get('formFields', [])
    filled_fields = []

    # print(form_fields)

    form_fields_json = json.dumps(form_fields, indent=4)
    user_data_json = json.dumps(user_data, indent=4)

    prompt_input = {
        "form_fields": form_fields_json,
        "user_data": user_data_json
    }

    response = llm_chain.invoke(prompt_input)
    response_content = response.content.strip()

    field_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "string"}
        },
        "required": ["name", "value"]
    }
    
    response_schema = {
        "type": "array",
        "items": field_schema
    }

    try:
        json_match = re.search(r'\[\s*{.*}\s*\]', response_content, re.DOTALL)
        if not json_match:
            raise ValueError("Invalid JSON format in LLM response.")
        filled_fields = json.loads(json_match.group())
        # validate(instance=filled_fields, schema=response_schema)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Error parsing or validating LLM response: {e}")
        return jsonify({"error": "Failed to process form fields due to invalid response format."}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

    # print(filled_fields)
    return jsonify({'filledFields': filled_fields})

@app.route('/resume', methods=['GET'])
def get_resume():
    global resume_path
    # Path to the resume file on the server
    resume_path = os.path.abspath(resume_path)
    return send_file(resume_path, as_attachment=True)

@app.route('/transcript', methods=['GET'])
def get_transcript():
    global transcript_path
    # Path to the resume file on the server
    transcript_path = os.path.abspath(transcript_path)
    return send_file(transcript_path, as_attachment=True)

if __name__ == '__main__':
# Making Sure the FIle are already there
    warnings.filterwarnings("ignore", category=DeprecationWarning) 
    text = "Running the Backend Server, You may Use Chrome Extension"
    print_in_box(text)
    app.run(debug=False)