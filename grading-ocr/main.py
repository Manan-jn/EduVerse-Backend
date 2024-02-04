from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image
import numpy as np
import os
import cv2
from pdfplumber import open as pdf_open
from skimage.color import rgb2gray
from skimage.transform import rotate
from deskew import determine_skew
from google.cloud import vision
from decouple import config
import requests
from openai import OpenAI
import uvicorn
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware


client = OpenAI(
  api_key="ENTER YOUR API KEY",
)
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/get_student_score/")
async def get_student_score_view(
    quiz_file: UploadFile = Form(...),
    answer_key_file: UploadFile = Form(...),
    student_answers: UploadFile = Form(...),
):
    try:
        quiz = BytesIO(await quiz_file.read())
        answer_key = BytesIO(await answer_key_file.read())
        student_answers_data = await student_answers.read()

        quiz_text = extract_text_from_pdf(quiz)
        answer_key_text = extract_text_from_pdf(answer_key)

        pil_image = Image.open(BytesIO(student_answers_data))
        pil_image_rgb = pil_image.convert('RGB')
        image_ndarray = np.array(pil_image_rgb)

        image = pre_process_image(image_ndarray)
        _, image = cv2.imencode('.png', image)
        image = image.tobytes()

        student_text = writing_to_text(image)

        student_score = get_student_score(quiz_text, answer_key_text, student_text)
        # student_score_data = print_resp(student_score)
        # student_score = student_score['choices'][0]['message']['content']

        return JSONResponse(content={'student_score': student_score})

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def extract_text_from_pdf(file):
    with pdf_open(file) as pdf:
        text = " ".join(page.extract_text() for page in pdf.pages)
    return text

def pre_process_image(img):
    img = rgb2gray(img)
    angle = determine_skew(img)
    img = rotate(img, angle, resize=True) * 255
    return img

def writing_to_text(image):
    client = vision.ImageAnnotatorClient.from_service_account_file('./clientid.json')
    img = vision.Image(content=image)
    response = client.document_text_detection(image=img)
    return response.full_text_annotation.text

def get_student_score(quiz, answer_key, student_answers):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are a professor who is grading a student's quiz. \
                The quiz questions, answer key, and student's answers are below:"},

            {"role": "user", "content": "In the quiz, the total number of points per question is \
                specified, and in the answer key, an explanation of what would be an acceptable \
                answer is described. Please evaluate the student's response and provide a score for \
                the quiz, with explanation on where the student went wrong in incorrect responses. \
                Give points awarded for each question. Keep in mind that the student answers will contain \
                only the answers in a numbered order where an answer number corresponds to the question \
                number from the quiz.\n" + "Quiz: " + quiz + "\n\nAnswer Key: " + answer_key + "\n\nStudent's Answers:" + student_answers},

            {"role": "assistant", "content": "Of course, here is the students responses structured in a \
                format as Quiz Name, and Total Points Possible on the quiz, followed by an array where each element is in form of  Question Nnumber, Points Scored per question \
                (if correct, full points; if partially correct, partial credit; if incorrect, 0 points), Feedback, Total Points scored where each line is separate by a new line:"
            }
        ]
        )
        return response.choices[0].message.content
        
    except Exception as e: 
        print(e)
        return "error"

def print_resp(input_string):
    arr = []
    first_question_index = input_string.find("Question")

    if first_question_index != -1:
        before_question = input_string[:first_question_index].strip()
        after_question = input_string[first_question_index:].strip()

        arr.append(before_question)

        split_strings = after_question.split("Question")
        split_strings = [f'Question {split_strings[s].strip()}' for s in range(1, len(split_strings))]

        split_strings = [s for s in split_strings if s]
        
        for i in range(len(split_strings)-1):
            arr.append(split_strings[i])

        temp = split_strings[-1].split("Quiz")
        arr.append(temp[0])

        if len(temp) > 1:
            arr.append("Quiz" + temp[1])

        temp = split_strings[-1].split("Total")
        if len(temp) > 1:
            arr.append("Total" + temp[1])
        
    return arr


@app.get('/')
def hello(request: Request):
    print('server is live')
    return {200: "API Running"}
