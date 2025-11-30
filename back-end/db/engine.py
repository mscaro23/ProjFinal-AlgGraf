from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("POSTGRES_USER", "")
PASSWORD = os.getenv("POSTGRES_KEY", "")
HOST = os.getenv("POSTGRES_HOST", "")
PORT = os.getenv("POSTGRES_PORT", "")
DATABASE = os.getenv("POSTGRES_DATABASE", "")
import logging

logging.info(f"USER: {USER}")

if not all([USER, PASSWORD, HOST, PORT, DATABASE]):
    raise ValueError(
        "Database environment variables are missing. "
        "Please set: POSTGRES_USER, POSTGRES_KEY, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE"
    )

DATABASE_URL = (
    f"postgresql+psycopg2://{USER}:{quote(PASSWORD)}@{HOST}:{PORT}/{DATABASE}"
)
engine = create_engine(DATABASE_URL, future=True, echo=False)
