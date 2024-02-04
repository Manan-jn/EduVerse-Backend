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

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


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

# Assuming you have an OpenAI API key, replace 'YOUR_OPENAI_API_KEY' with your actual key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model="gpt-3.5-turbo"

tip_prompt_student = """ 
        I am a student and my learning streak is {learning_streak}, I have learned for {hours_learned} hours, and I have completed {lectures_completed} lectures.
        Generate a tip for me on how to improve my learning. generate the tip only in 2-3 lines.
    """

tip_prompt_parent = """
        I am a parent and my child's learning streak is {learning_streak}, my child has learned for {hours_learned} hours, and my child has completed {lectures_completed} lectures.
        Generate a tip for me on how to improve my child's learning. generate the tip only in 2-3 lines.
    """
tip_prompt_teacher = """
        I am a teacher and I have uploaded {slides_uploaded} slides, and my students have learned for {total_hours_learned} hours.
        Generate a tip for me on how to improve my students' learning. generate the tip only in 2-3 lines.
    """

async def generate_tip_student(learning_streak, hours_learned, lectures_completed):
    # Define the prompt using the provided information

    try:
        response = openai.chat.completions.create(
            model=openai_model.lower(),
            messages=[
                {"role": "system", "content": tip_prompt_student.format(learning_streak=learning_streak, hours_learned=hours_learned, lectures_completed=lectures_completed)},
            ],
            max_tokens=400
        )
        print(response)
        return response.choices[0].message.content
        # # Extract and return the generated tip
        # generated_tip = response['choices'][0]['text'].strip()
        # return generated_tip

    except Exception as e:
        # Handle exceptions appropriately (e.g., logging, custom error messages)
        print(f"Error generating tip: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating tip")

async def generate_tip_parent(learning_streak, hours_learned, lectures_completed):
    # Define the prompt using the provided information

    try:
        response = openai.chat.completions.create(
            model=openai_model.lower(),
            messages=[
                {"role": "system", "content": tip_prompt_parent.format(learning_streak=learning_streak, hours_learned=hours_learned, lectures_completed=lectures_completed)},
            ],
            max_tokens=400
        )
        print(response)
        return response.choices[0].message.content
        # # Extract and return the generated tip
        # generated_tip = response['choices'][0]['text'].strip()
        # return generated_tip

    except Exception as e:
        # Handle exceptions appropriately (e.g., logging, custom error messages)
        print(f"Error generating tip: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating tip")
    

async def generate_tip_teacher(slides_uploaded, total_hours_learned):
    # Define the prompt using the provided information

    try:
        response = openai.chat.completions.create(
            model=openai_model.lower(),
            messages=[
                {"role": "system", "content": tip_prompt_teacher.format(slides_uploaded=slides_uploaded, total_hours_learned=total_hours_learned)},
            ],
            max_tokens=400
        )
        print(response)
        return response.choices[0].message.content
        # # Extract and return the generated tip
        # generated_tip = response['choices'][0]['text'].strip()
        # return generated_tip

    except Exception as e:
        # Handle exceptions appropriately (e.g., logging, custom error messages)
        print(f"Error generating tip: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating tip")

# Define the POST route
@app.post("/tipStudent")
async def tip_student(request: Request):
    try:
        # Get data from JSON payload
        data = await request.json()
        learning_streak = data.get('learning_streak', 0)
        hours_learned = data.get('hours_learned', 0)
        lectures_completed = data.get('lectures_completed', 0)

        # Generate tip using the provided information
        tip = await generate_tip_student(learning_streak, hours_learned, lectures_completed)

        # Return the generated tip as JSON response
        return JSONResponse(content={"tip": tip})

    except HTTPException as e:
        # Return HTTPException details as JSON response
        return JSONResponse(content={"error": str(e.detail)}, status_code=e.status_code)
    
# Define the POST route
@app.post("/tipParent")
async def tip_parent(request: Request):
    try:
        # Get data from JSON payload
        data = await request.json()
        learning_streak = data.get('learning_streak', 0)
        hours_learned = data.get('hours_learned', 0)
        lectures_completed = data.get('lectures_completed', 0)

        # Generate tip using the provided information
        tip = await generate_tip_parent(learning_streak, hours_learned, lectures_completed)

        # Return the generated tip as JSON response
        return JSONResponse(content={"tip": tip})

    except HTTPException as e:
        # Return HTTPException details as JSON response
        return JSONResponse(content={"error": str(e.detail)}, status_code=e.status_code)
    
# Define the POST route
@app.post("/tipTeacher")
async def tip_teacher(request: Request):
    try:
        # Get data from JSON payload
        data = await request.json()
        slides_uploaded = data.get('slides_uploaded', 0)
        total_hours_learned = data.get('total_hours_learned', 0)

        # Generate tip using the provided information
        tip = await generate_tip_teacher(slides_uploaded, total_hours_learned)

        # Return the generated tip as JSON response
        return JSONResponse(content={"tip": tip})

    except HTTPException as e:
        # Return HTTPException details as JSON response
        return JSONResponse(content={"error": str(e.detail)}, status_code=e.status_code)





