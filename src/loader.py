import json
import re

from model.module import File, Module
from model.sageclass import SageClass
from data import Data

import json
import os
import ast
from dotenv import load_dotenv
from pathlib import Path

class Loader:
    dotenv_path = Path('config.env')
    load_dotenv(dotenv_path=dotenv_path)
    SAGE_SRC = os.getenv("SAGE_SRC")

    @classmethod
    def pyfile_to_module(cls, path):
        # Convert file path to module name
        rel_path = os.path.relpath(path, cls.SAGE_SRC)
        no_ext = os.path.splitext(rel_path)[0]
        parts = no_ext.split(os.sep)
        return ".".join(["sage"] + parts)

    @classmethod
    def create_python_module_class_map(cls):
        module_class_map = {}
        for dirpath, _, filenames in os.walk(cls.SAGE_SRC):
            for filename in filenames:
                if filename.endswith(".py"):
                    full_path = os.path.join(dirpath, filename)

                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        try:
                            tree = ast.parse(f.read())
                        except SyntaxError:
                            continue  # Skip broken files

                    module_name = cls.pyfile_to_module(full_path)
                    classes = [
                        node.name for node in ast.walk(tree)
                        if isinstance(node, ast.ClassDef)
                    ]

                    if classes:
                        module_class_map[module_name] = classes

        return module_class_map

    @classmethod
    def initialize(cls):
        cls.load_all_modules()

    @classmethod
    def load_all_modules(cls):
        base_module = Module("sage", None)
        Data.add_module("sage", base_module)
        with open("python_modules.json") as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                if module_name.startswith("sage.src.sage."):
                    submodule_names = module_name.split(".")[3:]
                    parent_module = base_module
                    for submodule_name in submodule_names[:-1]:
                        submodule = Data.get_module(
                            parent_module.full_path_name + "." + submodule_name) \
                                or Module(submodule_name, parent_module)
                        Data.add_module(submodule.full_path_name, submodule)
                        parent_module = submodule
                    
                    file_name = submodule_names[-1]
                    file = Module(file_name, parent_module)
                    Data.add_module(file.full_path_name, file)

    @classmethod
    def load_all_classes(cls):
        pass

    @classmethod
    def parse_cython(cls, file_path: str):
        results = {
            "classes": [],          # (name, kind, lineno)
            "functions": [],        # (name, kind, lineno)
            "imports": [],          # (type, code, lineno)
        }

        class_pattern = re.compile(r"\s*(cdef\s+)?class\s+(\w+)")
        func_pattern = re.compile(r"\s*(cpdef|def)\s+\w+\s+(\w+)\s*\(")
        import_pattern = re.compile(r"\s*(from\s+[\w.]+\s+)?import\s+.*")
        cimport_pattern = re.compile(r"\s*from\s+[\w.]+\s+cimport\s+.*")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                # Class declarations
                if match := class_pattern.match(line):
                    kind = "cdef class" if match.group(1) else "class"
                    results["classes"].append((match.group(2), kind, i))

                # Function declarations
                elif match := func_pattern.match(line):
                    kind = match.group(1)  # 'cpdef' or 'def'
                    results["functions"].append((match.group(2), kind, i))

                # Import / from-import
                elif cimport_pattern.match(line):
                    results["imports"].append(("cimport", line.strip(), i))
                elif import_pattern.match(line):
                    results["imports"].append(("import", line.strip(), i))

        return results
