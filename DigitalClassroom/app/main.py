import os
import sys
import time
import asyncio
# import pymongo
import random
import requests
# from bson import Binary
import subprocess
import openai
import json
import re

import firebase_admin
from firebase_admin import credentials, storage

from dotenv import load_dotenv
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import PromptTemplate


from langchain.document_loaders.unstructured import UnstructuredFileLoader


load_dotenv()
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate_config_file():
    secrets = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id":os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
    }
    config_file_path = os.path.join(project_folder, "config.json")
    with open(config_file_path, "w") as json_file:
         json.dump(secrets, json_file)
    return "true"

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGE_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
}

project_folder = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(project_folder, "config.json")
cred = credentials.Certificate(config_file_path)
firebase_admin.initialize_app(cred, {"storageBucket": firebase_config["storageBucket"]})

persist_directory = 'db'
slide_hash = ""
saved_slides= ""
# Documents
# file_name = ""
documents = []

async def upload_file_to_storage(file_path, destination_path):
    # Create a storage client
    storage_client = storage.bucket()

    # Upload file to Firebase Storage
    blob = storage_client.blob(destination_path)
    blob.upload_from_filename(file_path)
    print(f"File {file_path} uploaded to {destination_path} successfully.")
    return "true"

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    file_contents = await file.read()
    # temp = await generate_config_file()

    # Specify the path where you want to save the file in the project folder
    file_path = os.path.join(project_folder, file.filename)
    # Write the file contents to the specified path
    with open(file_path, "wb") as f:
        f.write(file_contents)

    global loader, documents
    loader = UnstructuredFileLoader(file_path)
    documents = loader.load()
    print(documents)
    return {"message": f"File '{file.filename}' uploaded successfully"}

# Prompt
slides_prompt = """ 
    The following is the given textbook material:
    
    {text}
    
    For the textbook material above:
    1. Break this text into chunks of concepts, with each chunck contains pieces of text speaking about the same one concept. 
    2. For each such chunks, summarize the content, give online title about the core concept, with two to three bullet points about the details of the concept, each bullet point must not exceed 15 words.
    3. With this title, bullet, description for each chunk, wirte a slides for each chunk in Marp format. 
    
    Rules for slides in Marp format:
    1. Each --- indicates a new slide. Limit 50 words within each slides.
    2. # is for the title of each slide.
    3. - is for bullet point. 1., 2., 3. are numbered points.
    4. <image> (keyword: xxx) is an image illustrating the keyword "xxx". You must include one image for each slide. Make sure keyword "xxx" for each slide is different enough. The keyword "xxx" must be at least 10 words that summarize the entire slide.
    5. `` is for code.

    Following is an example for the above rules for the format:
    # Introduction to Marp

    Marp is a powerful tool that allows you to create presentations using simple Markdown syntax. You can easily create slides and format text with Marp.
    <image> (keyword: what is Marp)

    ---

    # Installing Marp

    To get started with Marp, you can install the Marp CLI or use Marp for Visual Studio Code extension.

    1. Marp CLI: `npm install -g @marp-team/marp-cli`
    2. Marp for Visual Studio Code: Install the extension from the Visual Studio Code marketplace.
    
    <image> (keyword: how to install Marp)

    Now ends with format introduction. 
    
    Output all the slides in 1100 tokens, but make sure they still cover all things in the input text.
    Make sure there are no space or tab before any line of your output.
    Here is your output of slides:
    """

SLIDES_PROMPT = PromptTemplate(
    template=slides_prompt, input_variables=["text"]
)

# chat history
chat_history = []


@app.get("/")
async def test(request: Request):
    """test"""
    return 'test'

def divide_into_chunks(text, chunk_size):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

openai_model="gpt-3.5-turbo"

def summarize_with_openai_api(text):
    try:
        response = openai.chat.completions.create(
            model=openai_model.lower(),
            messages=[
                {"role": "system", "content": slides_prompt},
                {"role": "user", "content": (text)}
            ],
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e: 
        print(e)
        return "error"

openai.api_key = os.getenv("OPENAI_API_KEY")
pattern = re.compile(r'<image>\s*\(keyword:\s*([^)]+)\)')
GOOGLE_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_ENGINE = os.getenv("SEARCH_ENGINE_ID")
URL = "https://www.googleapis.com/customsearch/v1"
transcript_url = "https://api.d-id.com/talks"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic YldGdVlXNHVibWwwWkd4QVoyMWhhV3d1WTI5dDptMFM1VFlGMC1aTUExUDlKbVFpZ1M="
}


md_file_path = ""

# mongo_uri = "mongodb://localhost:27017/"  # Change this to your MongoDB URI
# database_name = "my_db"  # Change this to your desired database name
# collection_name = "files" 

# def connect_to_mongodb():
#     try:
#         client = pymongo.MongoClient(mongo_uri)
#         print("Connected to MongoDB successfully!")
#         return client[database_name]
#     except pymongo.errors.ConnectionFailure as e:
#         print(f"Error connecting to MongoDB: {e}")
#         return None

# async def upload_file_to_mongodb(file_path, db, collection):
#     try:
#         with open(file_path, "rb") as file:
#              # Read the content of the file
#             file_content = file.read()
#             document = {"filename": os.path.basename(file_path), "data": file_content}
#             result =  collection.insert_one(document)
#             print(f"File uploaded successfully. Document ID: {result.inserted_id}")
#     except Exception as e:
#         print(f"Error uploading file to MongoDB: {e}")


def convert_to_pdf(input_file, output_file):
    try:
        # Use subprocess to call Marp CLI
        subprocess.run(['marp', '--allow-local-files', '--pdf', input_file, '-o', output_file], check=True)
        print(f'Successfully converted {input_file} to {output_file}')
    except subprocess.CalledProcessError as e:
        print(f'Error converting {input_file} to PDF. {e}')
@app.get("/")
async def test(request: Request):
    """test"""
    return 'test'

@app.get("/slides")
async def generate_response():
    # Initialize firebase
    chunk_size = 500  # Adjust as needed
    data = documents[0].page_content
    chunks = divide_into_chunks(data, chunk_size)

    summary = summarize_with_openai_api(data)
    slide_hash =  await convert_md(summary)
    print(slide_hash)
 
    # if db==None:
    #     return "Error connecting to MongoDB"
    # with open(md_file_path, "a") as global_file:
    #     for chunk in chunks:
    #         summary = summarize_with_openai_api(chunk)
    #         slide_hash = convert_md(summary)
    #         print(slide_hash)
    # collection = db[collection_name]
    # await upload_file_to_mongodb(md_file_path, db, collection)

    # Convert the file to PDF and save it to the fireabse
    # Get the transcript from the backend and get the video file save it to the firebase
    # Return the id of the saved database to the frontend
    return slide_hash

transcripts_prompt = """ 
    The following is the given textbook:
    
    {text}

    Textbook ends.

    The following is the given slides:

    """ + saved_slides + """

    Slides ends.
    
    Suppose you are a professor teaching a lecture using the given textbook and slides.
    You are humorous, yet professional in your way of teaching.
    
    You are going to write a speech draft for your lecture. 
    Each slide in the given slides start with --- and the title for this slides starts with #.
    Format your speech draft into sections where each section corresponds to a slide in the given slides. Each section starts with #section_number.
    For each bullet point in a slide, write two to three sentence using related information in the given textbook to explain what the bullet point means, and give example.
    
    Output your speech draft in 1000 tokens, but make sure they still cover all things in the input text.
    Write your speech draft here:
    """

TRANSCRIPTS_PROMPT = PromptTemplate(
    template=transcripts_prompt, input_variables=["text"]
)

def generate_transcript(text):
    try:
        response = openai.chat.completions.create(
            model=openai_model.lower(),
            messages=[
                {"role": "system", "content": transcripts_prompt},
                {"role": "user", "content": (text)}
            ],
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e: 
        print(e)
        return "error"


@app.get("/transcripts")
async def generate_response_for_transcripts():
    with open(md_file_path, "r") as file:
            md_content = file.read()
            print(md_content)
            transcript = generate_transcript(md_content)
            print(transcript)  
            return transcript
    # # Parse transcripts
    # pattern = r"#section_\d+\n(.+?)(?=\n#section_\d+|\Z)"
    # transcript_sections = re.findall(pattern, transcripts, flags=re.DOTALL)

    # created_time = int(time.time())
    # response_data = {
    #     "created": created_time,
    #     "model": "prof-ai-v1",
    #     "content": transcript_sections
    # }
    return "text"


async def convert_md(file_string):
    # connect_to_mongodb()
    replaced_file_string = replace_image_with_url(get_images_by_keywords(find_image_keywords(file_string)), file_string)
    hash = random.getrandbits(128)
    print("hash value: %032x" % hash)
    newmd_file_path = os.path.join(project_folder, f"{hash}.md")
    md_file_path = newmd_file_path
    newpdf_file_path = os.path.join(project_folder, f"{hash}.pdf")
    destination_path_in_storage = f"slides/{hash}.md"
    f = open(newmd_file_path, "w")
    f.write(replaced_file_string)
    f.close()
    # await upload_file_to_mongodb(newmd_file_path, database_name, collection_name)
    # process = await asyncio.create_subprocess_exec(
    #     "marp", newmd_file_path, "-o", newpdf_file_path
    # )
    # # Wait for the subprocess to complete
    # await process.wait()
    #     # Check if the PDF file was generated successfully
    # if process.returncode != 0:
    #     raise subprocess.CalledProcessError(process.returncode, "marp")
    
    # print("File converted successfully.")
    await upload_file_to_storage(newmd_file_path, destination_path_in_storage)
    with open(newmd_file_path, "r") as file:
            md_content = file.read()
            transcript = generate_transcript(md_content)
            print(transcript)  
    return str(hash)

def replace_image_with_url(res, file_string):
    for key in res:
        side = "left"
        url = res[key][0]
        if random.randint(0, 1) == 0:
            side = "right"
        if res[key][1] > res[key][2]:
            format_image = f"bg fit {side}:{random.randint(20,40)}%"
        else:
            format_image = f"bg fit {side}"
        file_string = file_string.replace(f"<image> (keyword: {key})", f"![{format_image}]({url})")
        print(f"{key}: {url}")
    return file_string


def find_image_keywords(file_string):
    return re.findall(r'<image> \(keyword: (.*?)\)', file_string)


def get_images_by_keywords(queries):
    res = {}
    for query in queries:
        res[query] = get_image(query)
    return res


# Fetch an image from Google Custom Search API
def get_image(query):
    load_dotenv()
    pse_id = SEARCH_ENGINE
    params = {
        'cx': pse_id,
        'num': '5',
        'q': query + ' concept explained',
        'searchType': 'image',
        'key': GOOGLE_API_KEY,
        'imgSize': 'medium',
    }
    response = requests.get('https://www.googleapis.com/customsearch/v1', params=params)
    data = response.json()
    res = random.choice(data['items'])
    return res['link'], res['image']['height'], res['image']['width']