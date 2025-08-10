import json
import subprocess
from pathlib import Path

class Settings:
    @classmethod
    def initialize(cls):
        this_dir = Path(__file__).parent
        project_root = this_dir.parent.parent
        cls._config_file = project_root/"config.json"
        with open(cls._config_file, "r") as f:
            config = json.loads(f.read())
        
        def get_path(pathname: str):
            base_dir = project_root
            if pathname.startswith("/"):
                return Path(pathname)
            while pathname.startswith("../"):
                base_dir = base_dir.parent
                pathname = pathname[3:]
            return base_dir/pathname

        cls.SAGE_BASE = get_path(config.get("sage_path",  "../sage"))
        # If Sage is not installed at this location, install it
        if not cls.SAGE_BASE.is_dir():
            do_clone = input(f"Sage installation not found at {cls.SAGE_BASE}. Would you like to clone it? [y/n]").lower()
            while do_clone not in "yn":
                do_clone = input(f"Please respond with [y/n]").lower()
            
            if do_clone == "y":
                subprocess.run(["git", "clone", "https://github.com/sagemath/sage.git", cls.SAGE_BASE], check=True)
            else:
                print("Parts of sage-deps will not work without a local copy of the Sage repository.")
                print("You can specify the Sage installation location by running `sdeps -set-config sage_path <sage-path>`.")

        cls.SAGE_SRC = cls.SAGE_BASE/"src"/"sage"
        cls.MODULE_JSON_SRC = get_path(config.get("modules_src",  "resources/modules.json"))
        cls.MODULE_JSON_SRC_TEST = project_root/"resources"/"modules_tmp.json"
        cls.IMPORT_MAP_SRC = project_root/"resources"/"imports.json"
        cls.DEPENDENCIES_JSON = project_root/"resources"/"dependencies.json"
        cls.GRAPH_DIR = get_path(config.get("graph_src", "graphics"))
        cls.GRAPH_JSON = cls.GRAPH_DIR/"graph.json"
        cls.FILTER_JSON = get_path(config.get("filter_src", "resources/filter.json"))
        cls.COMMIT_HISTORY = project_root/"resources"/"commits.txt"
        cls.COMMIT_METADATA = project_root/"resources"/"commit_metadata.json"
        cls.LOCAL_DOC_ROOT = cls.SAGE_BASE/"src"/"doc"/"en"/"reference"
        cls.DOC_BASE_URL = "https://doc.sagemath.org/html/en/reference"
    
    @classmethod
    def set_config(cls, name, value):
        with open(cls._config_file, "r") as f:
            config = json.loads(f.read())
        
        config[name] = value

        with open(cls._config_file, "w") as f:
            config = f.write(json.dumps(config, 4))

Settings.initialize()