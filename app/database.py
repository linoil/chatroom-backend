from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
# connect_args = {"check_same_thread": False}
# engine = create_engine(DATABASE_URL, connect_args=connect_args)
engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine, checkfirst=True)

def get_session():
    with Session(engine) as session:
        yield session
