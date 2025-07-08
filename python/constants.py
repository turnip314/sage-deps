from pathlib import Path
this_dir = Path(__file__).parent

SAGE_BASE = this_dir.parent.parent/"sage"
SAGE_SRC = SAGE_BASE/"src"/"sage"
MODULE_JSON_SRC = this_dir.parent.parent/"modules.json"
MODULE_JSON_SRC_TEST = this_dir.parent/"resources"/"modules.json"
IMPORT_MAP_SRC = this_dir.parent/"resources"/"imports.json"
DEPENDENCIES_JSON = this_dir.parent/"resources"/"dependencies.json"
GRAPH_JSON = this_dir.parent/"graphics"/"graph.json"
COMMIT_HISTORY = this_dir.parent/"resources"/"commits.txt"
COMMIT_METADATA = this_dir.parent/"resources"/"commit_metadata.json"
LOCAL_DOC_ROOT = SAGE_BASE/"src"/"doc"/"en"/"reference"
DOC_BASE_URL = "https://doc.sagemath.org/html/en/reference"
