# Refer to the repo: https://github.com/darcyg32/Ollama-FastAPI-Integration-Demo.git

import os
import json
import requests
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

app = FastAPI()

# Define a data model using Pydantic for the request body
class GenerateRequest(BaseModel):
    model: str              # Name of the model to be used
    prompt: str             # Prompt to be sent to the model
    stream: bool = False    # Flag to enable streaming of responses

# Use the environment variable OLLAMA_API_URL or fallback to localhost
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

@app.post("/api/generate")
async def generate_text_api(request: GenerateRequest):
    """
    This endpoint accepts a POST request containing a prompt.
    It sends the prompt to the Ollama API and returns the API's response.
    """
    url = OLLAMA_API_URL                            # URL of the local model API
    headers = {"Content-Type": "application/json"}  # Specify the content type as JSON
    data = {
        "model": request.model,     # Model name from the request
        "prompt": request.prompt,   # Prompt from the request
        "stream": request.stream    # Streaming flag from the request
    }
    async with httpx.AsyncClient() as client:
        try:
            # Forward the prompt to the Ollama API
            response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
            response.raise_for_status()         # Raises an exception for 4xx/5xx responses
            raw_response = response.json()      # Parse the JSON response from Ollama
        except httpx.RequestError as exc:
            # Handle errors during the request
            raise HTTPException(status_code=500, detail=f"Error connecting to Ollama API: {exc}")
        except httpx.HTTPStatusError as exc:
            # Handle non-successful HTTP responses
            raise HTTPException(status_code=exc.response.status_code, detail=f"Ollama API error: {exc}")

    # Return the result from the Ollama API to the user
    return raw_response
