# Refer to the repo: https://github.com/darcyg32/Ollama-FastAPI-Integration-Demo.git

import os
import json
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Literal, Annotated
from sqlmodel import Session, select

from models import ChatSession
from database import init_db, get_session

# Load environment variables from .env file if present
load_dotenv()

app = FastAPI()

SessionDep = Annotated[Session, Depends(get_session)]

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()
origins = [
    "http://localhost:5173",  # vite server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define a data model using Pydantic for the request body
class GenerateRequest(BaseModel):
    model: str  # Name of the model to be used
    prompt: str  # Prompt to be sent to the model
    stream: bool = False  # Flag to enable streaming of responses


class ChatRequest(BaseModel):
    model: str
    messages: List[dict]
    stream: bool = True


# Use the environment variable OLLAMA_API_URL or fallback to localhost
GEN_URL = os.getenv("OLLAMA_GEN_URL", "http://localhost:11434/api/generate")
CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")

# curl -X POST "http://localhost:8000/api/generate" -H "Content-Type: application/json" -d @data.json


@app.post("/api/generate")
async def generate_text_api(request: GenerateRequest):
    """
    This endpoint accepts a POST request containing a prompt.
    It sends the prompt to the Ollama API and returns the API's response.
    """
    url = GEN_URL  # URL of the local model API
    data = {
        "model": request.model,  # Model name from the request
        "prompt": request.prompt,  # Prompt from the request
        "stream": request.stream,  # Streaming flag from the request
    }
    async with httpx.AsyncClient() as client:
        try:
            # Forward the prompt to the Ollama API
            response = await client.post(url, json=data)
            response.raise_for_status()  # Raises an exception for 4xx/5xx responses
            return response.json()  # Parse the JSON response from Ollama
        except httpx.RequestError as exc:
            # Handle errors during the request
            raise HTTPException(
                status_code=500, detail=f"Error connecting to Ollama API: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            # Handle non-successful HTTP responses
            raise HTTPException(
                status_code=exc.response.status_code, detail=f"Ollama API error: {exc}"
            )


async def stream_chat_response(request_data: dict):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", CHAT_URL, json=request_data) as response:
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to stream response from Ollama",
                    )

                async for chunk in response.aiter_raw():
                    try:
                        json_data = json.loads(chunk)
                        done = "done" in json_data and json_data["done"]
                        if "message" in json_data and "content" in json_data["message"]:
                            yield (json.dumps({
                                "content": json_data["message"]["content"],
                                "done": done,
                            }) + "\n").encode("utf-8")
                            
                    except json.JSONDecodeError:
                        continue

    except asyncio.CancelledError:
        print("Client disconnected, stopping stream.")
    except httpx.RequestError as e:
        print(f"Request error: {e}")


# curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d @messages.json


@app.post("/chat")
async def chat_with_model(request: ChatRequest):
    request_data = request.model_dump()

    # streaming
    if request.stream:
        return StreamingResponse(
            stream_chat_response(request_data), media_type="application/x-ndjson"
        )

    # # non-streaming
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(CHAT_URL, json=request_data)
    #     if response.status_code != 200:
    #         raise HTTPException(status_code=response.status_code, detail="Failed to get response from Ollama")

    #     json_data = response.json()
    #     return json_data["message"]["content"].encode("utf-8")


# chat session
@app.post("/sessions/")
def create_chat_session(
    chat_session: ChatSession, 
    session: SessionDep
) -> ChatSession:
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session

@app.get("/sessions/list")
def get_user_sessions(
    session: SessionDep
) -> List[ChatSession]:
    result = session.execute(select(ChatSession))
    # return result
    return result.scalars().all()