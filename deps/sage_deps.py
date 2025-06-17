import json
import os
from dotenv import load_dotenv
from pathlib import Path

from parser import Parser

dotenv_path = Path('config.env')
load_dotenv(dotenv_path=dotenv_path)
MODULE_JSON_SRC = os.getenv("MODULE_JSON_SRC")

class_map = Parser.create_python_module_class_map()
class_map_json = json.dumps(class_map, indent=4)
with open(MODULE_JSON_SRC, "w") as f: 
    f.write(class_map_json)
