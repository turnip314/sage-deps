import json
import os
import ast
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('config.env')
load_dotenv(dotenv_path=dotenv_path)
SAGE_SRC = os.getenv("SAGE_SRC")

def pyfile_to_module(path):
    # Convert file path to module name
    rel_path = os.path.relpath(path, SAGE_SRC)
    no_ext = os.path.splitext(rel_path)[0]
    parts = no_ext.split(os.sep)
    return ".".join(["sage"] + parts)

def create_module_class_map():
    module_class_map = {}
    for dirpath, _, filenames in os.walk(SAGE_SRC):
        for filename in filenames:
            if filename.endswith(".py"):
                full_path = os.path.join(dirpath, filename)

                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    try:
                        tree = ast.parse(f.read())
                    except SyntaxError:
                        continue  # Skip broken files

                module_name = pyfile_to_module(full_path)
                classes = [
                    node.name for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                ]

                if classes:
                    module_class_map[module_name] = classes

    return module_class_map

if __name__ == "__main__":
    map = create_module_class_map()
    with open("deps_tree.json", mode="w") as f:
        f.write(json.dumps(map, indent=4))