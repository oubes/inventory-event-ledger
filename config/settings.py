# ---- Imports ---- #
from pathlib import Path
import os
from dotenv import load_dotenv

# ---- Load Environment Variables ---- #
load_dotenv()

# ---- Base Directory (project root) ---- #
BASE_DIR = Path(__file__).resolve().parent.parent

# ---- Env Variable ---- #
_raw_file_path = os.getenv("FILE_PATH")

if not _raw_file_path:
    raise ValueError("FILE_PATH is not set in .env")

# ---- Resolve Path ---- #
FILE_PATH: Path = (BASE_DIR / _raw_file_path).resolve()