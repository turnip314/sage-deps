import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).parent / "config.env"
load_dotenv(dotenv_path=dotenv_path)

SAGE_SRC = os.getenv("SAGE_SRC")
SAGE_BASE = os.getenv("SAGE_BASE")
MODULE_JSON_SRC = os.getenv("MODULE_JSON_SRC")
MODULE_JSON_SRC_TEST = os.getenv("MODULE_JSON_SRC_TEST")
IMPORT_MAP_SRC = os.getenv("IMPORT_MAP_SRC")
DEPENDENCIES_JSON = os.getenv("DEPENDENCIES_JSON")
GRAPH_JSON = os.getenv("GRAPH_JSON")
COMMIT_HISTORY = os.getenv("COMMIT_HISTORY")
COMMIT_METADATA = os.getenv("COMMIT_METADATA")
LOCAL_DOC_ROOT = os.getenv("LOCAL_DOC_ROOT")
DOC_BASE_URL = "https://doc.sagemath.org/html/en/reference"
