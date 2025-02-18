from contextlib import asynccontextmanager
import os
import json
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Annotated
from sqlmodel import Session, select, col

from models.ai import ChatRequest
from models.db import (
    ChatSessionTable,
    ChatSessionCreate,
    ChatSessionPublic,
    ChatSessionUpdate,
    ChatMessageTable,
    ChatMessageCreate,
    ChatMessagePublic,
)
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
@app.post("/sessions/", response_model=ChatSessionPublic, status_code=201)
def create_chat_session(chat_session: ChatSessionCreate, session: SessionDep):
    db_chat_session = ChatSessionTable.model_validate(chat_session)
    session.add(db_chat_session)
    session.commit()
    session.refresh(db_chat_session)
    return db_chat_session


@app.get("/sessions/", response_model=List[ChatSessionPublic])
def read_all_sessions(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    statement = (
        select(ChatSessionTable)
        .order_by(col(ChatSessionTable.created_at))
        .offset(offset)
        .limit(limit)
    )
    chat_sessions = session.exec(statement)
    return chat_sessions.all()


@app.get("/sessions/{id}", response_model=ChatSessionPublic)
def read_single_session(id: int, session: SessionDep):
    chat_session = session.get(ChatSessionTable, id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return chat_session


@app.put("/sessions/{id}", response_model=ChatSessionPublic)
def update_chat_session(id: int, chat_session: ChatSessionUpdate, session: SessionDep):
    db_chat_session = session.get(ChatSessionTable, id)
    if db_chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    updated_chat_session_data = chat_session.model_dump(exclude_none=True)
    db_chat_session.sqlmodel_update(updated_chat_session_data)
    session.add(db_chat_session)
    session.commit()
    session.refresh(db_chat_session)
    return db_chat_session


@app.delete("/sessions/{id}", status_code=204)
def delte_chat_session(id: int, session: SessionDep):
    chat_session = session.get(ChatSessionTable, id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    session.delete(chat_session)
    session.commit()
    return {}


# chat message
@app.post("/messages/", response_model=ChatMessagePublic)
def create_message(chat_message: ChatMessageCreate, session: SessionDep):
    db_chat_message = ChatMessageTable.model_validate(chat_message)
    session.add(db_chat_message)
    session.commit()
    session.refresh(db_chat_message)
    return db_chat_message


@app.get("/messages/", response_model=List[ChatMessagePublic])
def read_session_messages(session: SessionDep, session_id: int):
    try:
        chatSession = session.exec(
            select(ChatSessionTable).where(ChatSessionTable.id == session_id)
        ).one() 
        return sorted(chatSession.messages, key=lambda x: x.created_at)


    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Chat session not found")
