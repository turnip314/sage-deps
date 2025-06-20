import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).parent / "config.env"
load_dotenv(dotenv_path=dotenv_path)

SAGE_SRC = os.getenv("SAGE_SRC")
MODULE_JSON_SRC = os.getenv("MODULE_JSON_SRC")
IMPORT_MAP_SRC = os.getenv("IMPORT_MAP_SRC")
DEPENDENCIES_JSON = os.getenv("DEPENDENCIES_JSON")

print("SAGE_SRC:", SAGE_SRC)
print("MODULE_JSON_SRC:", MODULE_JSON_SRC)
