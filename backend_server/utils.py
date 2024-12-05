import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
# from langchain import ConversationChain
from langchain.chains import ConversationChain
import PyPDF2
from dotenv import load_dotenv
import os
import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from PIL.Image import Resampling
import time

# Loading the Open AI API Key
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_1', '')


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Update the required_fields dictionary with the extracted data
def update_fields(original, updates):
    for key, value in updates.items():
        if isinstance(value, dict):
            update_fields(original[key], value)
        else:
            if value:
                original[key] = value

# Function to get missing fields
def get_missing_fields(data):
    missing = []
    for key, value in data.items():
        if isinstance(value, dict):
            sub_missing = get_missing_fields(value)
            for item in sub_missing:
                missing.append(f"{key} -> {item}")
        else:
            if not value:
                missing.append(key)
    return missing


# Collect user inputs via enhanced GUI
def collect_user_inputs_gui(missing_fields):
    root = tk.Tk()
    root.title("AutoApplyAI: Missing Information")

    # Use ttk for better-looking widgets
    style = ttk.Style()
    style.theme_use('default')
    
    # Create a frame to hold the widgets
    main_frame = ttk.Frame(root, padding=(20, 20, 20, 20))
    main_frame.pack(fill='both', expand=True)

    # Load and add the logo at the top
    try:
        # Replace 'path_to_logo.png' with the actual path to your logo image
# Build the path to the image
        ss = "d:\\Semester_Data\\Semester_9\\LLM\\AutoApplyAI\\backend_server\\test.ipynb"
        script_dir = os.path.dirname(os.path.abspath(ss))
        image_path = os.path.join(script_dir, '..', 'chrome_extension', 'icons', 'icon128.png')
        image_path = os.path.abspath(image_path)

        logo_image = Image.open(image_path)
        # Optionally, resize the logo to fit the header
        logo_image = logo_image.resize((100, 100), Resampling.LANCZOS)  # Adjust size as needed
        logo_photo = ImageTk.PhotoImage(logo_image)
        
        # Create a label for the logo
        logo_label = ttk.Label(main_frame, image=logo_photo)
        logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
        logo_label.pack(pady=(0, 20))  # Add some padding below the logo
    except Exception as e:
        print(f"Error loading logo image: {e}")
        # Optionally, you can create a text header instead
        header_label = ttk.Label(main_frame, text="AutoApplyAI", font=("Helvetica", 16, "bold"))
        header_label.pack(pady=(0, 20))



    # Create a canvas and scrollbar for scrolling
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        '<Configure>',
        lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    entries = {}
    row = 0

    for field in missing_fields:
        # Simplify field name for display
        display_name = field.split(' -> ')[-1]
        display_name = display_name.replace('_', ' ').replace('-', ' ').title()
        question_text = f"Please enter your {display_name}:"

        # Create label and entry
        label = ttk.Label(scrollable_frame, text=question_text)
        label.grid(row=row, column=0, sticky='w', padx=5, pady=5)
        entry = ttk.Entry(scrollable_frame, width=50)
        entry.grid(row=row, column=1, padx=5, pady=5)
        entries[field] = entry
        row += 1

    # Add a submit button
    def on_submit():
        user_inputs = {}
        for field, entry in entries.items():
            value = entry.get()
            user_inputs[field] = value
        root.destroy()
        root.user_inputs = user_inputs

    submit_button = ttk.Button(main_frame, text="Submit", command=on_submit)
    submit_button.pack(pady=10)

    canvas.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    root.mainloop()
    return root.user_inputs


# Data Extraction of User from Resume and Analysis
def data_extraction_user(pdf_path):
    resume_text = extract_text_from_pdf(pdf_path)
    with open('user_data/file.json', 'r') as f:
        required_fields = json.load(f)
    llm = ChatOpenAI(temperature=0, api_key= OPENAI_API_KEY)
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False  # Set to True to see the conversation
    )

    extraction_prompt = f"""
    You are an intelligent assistant that extracts and infers information from resumes intelligently and effectively.

    Given the following resume text, extract the information and fill in the corresponding fields in the JSON structure below. Make sure to fill the fields in accordance to the common job application requried input style/format (Example, phone number should be in simple format without any dashes or brackets). Use your knowledge to infer missing fields when possible. Additionally, You can add more entries like if there are more than one education or work experience. The Entries whose data is not availabe leave those entries. While filling those that are available. Try to fill as much data as possible. 

    Resume Text:
    {resume_text}

    Required JSON Structure:
    {json.dumps(required_fields, indent=4)}

    Provide the filled JSON output with extracted and inferred information.
    """

    initial_response = conversation.predict(input=extraction_prompt)
    extracted_data = json.loads(initial_response)
    update_fields(required_fields, extracted_data)
    missing_fields = get_missing_fields(required_fields)
    user_inputs = collect_user_inputs_gui(missing_fields)

    # Feed back to LLM for cross-checking
    cross_check_prompt = f"""
    The User has provided further details for his profile, using the following information update the JSON fields:

    {json.dumps(user_inputs, indent=4)}

    Required JSON Fields:
    {json.dumps(required_fields, indent=4)}

    Please review the information, make any necessary inferences, and fill in any remaining missing fields intelligently. Make sure to fill the fields in accordance to the common job application requried input style/format.

    Provide the final updated JSON structure.

    **Important:** Output only the JSON data, without additional explanations.
    """

    final_response = conversation.predict(input=cross_check_prompt)
    extracted_data_final = json.loads(final_response)

    with open("user_data/user_data.json", "w") as outfile: 
        json.dump(extracted_data_final, outfile, indent = 4)


def check_resume_and_transcript():
    while True:
        # Check for resume and transcript PDFs
        files_in_directory = os.listdir('user_data/')
        resume_path = None
        transcript_path = None
        
        for file in files_in_directory:
            if file.endswith('.pdf'):
                if 'resume' in file.lower():
                    resume_path = os.path.join('user_data', file)
                elif 'transcript' in file.lower():
                    transcript_path = os.path.join('user_data', file)
        
        # Check if both PDF files are found
        if resume_path and transcript_path:
            text = f"Found resume: {resume_path}"
            print_in_box(text)
            text = f"Found transcript: {transcript_path}"
            print_in_box(text)
            return resume_path, transcript_path
        else:
            print("Required PDF files ('resume' and 'transcript') are missing. Please upload them.")
            time.sleep(5)  # Wait before asking again


def check_user_data_json(pdf_path):
    # Check if 'user_data/user_data.json' exists
    user_data_json_path = 'user_data/user_data.json'
    
    if os.path.exists(user_data_json_path):
        text = "User Data Found"
        print_in_box(text)
    else:
        text = "User Data is missing. Calling data_extraction_user()...."
        print_in_box(text)
        data_extraction_user(pdf_path)
        text = "User Data Extracted."
        print_in_box(text)

def print_in_box(text):
    # Calculate the width of the box
    box_width = len(text) + 6  # 2 spaces for padding on each side + 2 for the box borders
    print('+' + '-' * (box_width - 2) + '+')
    print(f"|  {text}  |")
    print('+' + '-' * (box_width - 2) + '+')



