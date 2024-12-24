from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
import google.generativeai as genai

import io
import os
import json
import time

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY not found in environment variables.")

# Configure Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()


@app.get("/")
async def health_check():
    return "The health check is successful!"


@app.get("/get-env/{key_name}")
async def health_check(key_name: str):
    value = os.getenv(key_name, None)
    return {"key": key_name, "value": value}


@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    try:
        start_time = time.time()
        # Read the file's content into memory
        file_content = await file.read()
        file_like_object = io.BytesIO(
            file_content
        )  # Create an in-memory file-like object

        # Get the MIME type of the uploaded file
        mime_type = file.content_type  # e.g., "image/jpeg" or "image/png"

        # Upload the file using genai.upload_file with the file-like object
        sample_file = genai.upload_file(
            path=file_like_object,  # Pass the in-memory file-like object
            mime_type=mime_type,  # Explicitly set the MIME type
            display_name=file.filename,
        )

        # Choose a Gemini API model.
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

        # Prompt the model with text and the previously uploaded image.
        response = model.generate_content(
            [
                sample_file,
                "Extract the km and time from the image and provide output in a json structure",
            ]
        )

        # Clean up the response text
        raw_response = response.text.strip()  # Remove any leading/trailing whitespace
        cleaned_string = (
            raw_response.strip("```").strip().replace("json\n", "").strip()
        )  # Remove backticks and further clean the string

        # Parse the cleaned string into a Python dictionary
        output = json.loads(cleaned_string)
        print("Time Taken for Execution : ", time.time() - start_time)
        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload_image_query")
async def upload_image_query(prompt: str, file: UploadFile = File(...)):
    try:
        start_time = time.time()
        # Read the file's content into memory
        file_content = await file.read()
        file_like_object = io.BytesIO(
            file_content
        )  # Create an in-memory file-like object

        # Get the MIME type of the uploaded file
        mime_type = file.content_type  # e.g., "image/jpeg" or "image/png"

        # Upload the file using genai.upload_file with the file-like object
        sample_file = genai.upload_file(
            path=file_like_object,  # Pass the in-memory file-like object
            mime_type=mime_type,  # Explicitly set the MIME type
            display_name=file.filename,
        )

        # Choose a Gemini API model.
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

        # Prompt the model with text and the previously uploaded image.
        response = model.generate_content([sample_file, prompt])

        if (
            prompt
            == "Extract the km and time from the image and provide output in a json structure"
        ):
            # Clean up the response text
            raw_response = (
                response.text.strip()
            )  # Remove any leading/trailing whitespace
            cleaned_string = (
                raw_response.strip("```").strip().replace("json\n", "").strip()
            )  # Remove backticks and further clean the string

            # Parse the cleaned string into a Python dictionary
            output = json.loads(cleaned_string)
            print("Time Taken for Execution : ", time.time() - start_time)
            return output

        return response.text

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
