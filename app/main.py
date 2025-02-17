# Refer to the repo: https://github.com/darcyg32/Ollama-FastAPI-Integration-Demo.git

from contextlib import asynccontextmanager
import os
import json
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Annotated
from sqlmodel import Session, select

from models import ChatSession
from database import init_db, get_session

# Load environment variables from .env file if present
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up section
    init_db()
    yield
    # clean up section should reside here


app = FastAPI(lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_session)]

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


class ChatRequest(BaseModel):
    model: str
    messages: List[dict]
    stream: bool = True


# Use the environment variable OLLAMA_CHAT_URL or fallback to localhost
CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")


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
                            yield (
                                json.dumps(
                                    {
                                        "content": json_data["message"]["content"],
                                        "done": done,
                                    }
                                )
                                + "\n"
                            ).encode("utf-8")

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


# chat session
@app.post("/sessions/")
def create_chat_session(chat_session: ChatSession, session: SessionDep) -> ChatSession:
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session


@app.get("/sessions/list")
def get_user_sessions(session: SessionDep) -> List[ChatSession]:
    result = session.execute(select(ChatSession))
    # return result
    return result.scalars().all()
