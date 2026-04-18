import os
from dotenv import load_dotenv

load_dotenv()

FILE_PATH: str = os.getenv("FILE_PATH") # type: ignore

if not FILE_PATH:
    raise ValueError("FILE_PATH is not set in .env")