from pathlib import Path
this_dir = Path(__file__).parent
project_root = this_dir.parent.parent

SAGE_BASE = project_root.parent/"sage"
SAGE_SRC = SAGE_BASE/"src"/"sage"
MODULE_JSON_SRC = project_root/"resources"/"modules.json"
MODULE_JSON_SRC_TEST = project_root/"resources"/"modules_tmp.json"
IMPORT_MAP_SRC = project_root/"resources"/"imports.json"
DEPENDENCIES_JSON = project_root/"resources"/"dependencies.json"
GRAPH_DIR = project_root/"graphics"
GRAPH_JSON = GRAPH_DIR/"graph.json"
FILTER_JSON = project_root/"resources"/"filter.json"
COMMIT_HISTORY = project_root/"resources"/"commits.txt"
COMMIT_METADATA = project_root/"resources"/"commit_metadata.json"
LOCAL_DOC_ROOT = SAGE_BASE/"src"/"doc"/"en"/"reference"
DOC_BASE_URL = "https://doc.sagemath.org/html/en/reference"
