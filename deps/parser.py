import json
import re

from data import Data
from loader import Loader
from model.dependency import Relation
from model.module import File, Module
from model.sageclass import SageClass

import json
import os
import ast
from dotenv import load_dotenv
from pathlib import Path

class Parser:
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
    def create_python_module_class_map(cls, python=True, cython=True):
        module_class_map = {}
        for dirpath, _, filenames in os.walk(cls.SAGE_SRC):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                module_name = cls.pyfile_to_module(full_path)
                if python and filename.endswith(".py"):
                    parsed_python = cls.parse_python(full_path)
                    module_class_map[module_name] = {}
                    module_class_map[module_name]["classes"] = [
                        { 
                            "classname": c["name"],
                            "imports": [
                                cls.resolve_import(imp[1], module_name) for imp in c["imports"]
                            ],
                            "inheritance": [] 
                        } for c in parsed_python["classes"] 
                    ]
                    module_class_map[module_name]["imports"] =[
                        cls.resolve_import(imp[1], module_name) for imp in parsed_python["imports"]
                    ]
                    module_class_map[module_name]["extension"] = ".py"

                elif cython and filename.endswith(".pyx"):
                    parsed_cython = cls.parse_cython(full_path)
                    module_class_map[module_name] = {}
                    module_class_map[module_name]["classes"] = [
                        { 
                            "classname": c["name"],
                            "imports": [
                                cls.resolve_import(imp[1], module_name) for imp in c["imports"]
                            ],
                            "inheritance": [] 
                        } for c in parsed_cython["classes"] 
                    ]
                    module_class_map[module_name]["imports"] =[
                        cls.resolve_import(imp[1], module_name) for imp in parsed_cython["imports"]
                    ]
                    module_class_map[module_name]["extension"] = ".pyx"

        return module_class_map

    @classmethod
    def parse_cython(cls, file_path: str):
        results = {
            "classes": [],          # {kind: str, name: str, line: int, functions: list, imports: list}
            "functions": [],        # (name, kind, lineno), top level functions only
            "imports": [],          # (type, code, lineno), top level imports only
        }

        class_pattern = re.compile(r"\s*(cdef\s+)?class\s+(\w+)")
        func_pattern = re.compile(r"\s*(cpdef|def)\s+\w+\s+(\w+)\s*\(")
        import_pattern = re.compile(r"\s*(from\s+[\w.]+\s+)?import\s+.*")
        cimport_pattern = re.compile(r"\s*from\s+[\w.]+\s+cimport\s+.*")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            last_class = None
            for i, line in enumerate(f, 1):
                # Check for unindent
                if line and (
                    line.startswith("def") or 
                    line.startswith("cdef") or 
                    line.startswith("from") or 
                    line.startswith("import") or 
                    line.startswith("class")
                ):
                    last_class = None

                # Class declarations
                if match := class_pattern.match(line):
                    last_class = {
                        "kind" : "cdef class" if match.group(1) else "class",
                        "name": match.group(2),
                        "line": i,
                        "functions": [],
                        "imports": []
                    }
                    results["classes"].append(last_class)

                # Function declarations
                elif match := func_pattern.match(line):
                    kind = match.group(1)  # 'cpdef' or 'def'
                    func = (match.group(2), kind, i)
                    if last_class is None:
                        results["functions"].append(func)
                    else:
                        last_class["functions"].append(func)

                # Import / from-import
                elif cimport_pattern.match(line):
                    imp = ("cimport", line.strip(), i)
                    if last_class is None:
                        results["imports"].append(imp)
                    else:
                        last_class["imports"].append(imp)
                elif import_pattern.match(line):
                    imp = ("import", line.strip(), i)
                    if last_class is None:
                        results["imports"].append(imp)
                    else:
                        last_class["imports"].append(imp)

        return results
    
    @classmethod
    def parse_python(cls, file_path: str):
        results = {
            "classes": [],          # {kind: str, name: str, line: int, functions: list, imports: list}
            "functions": [],        # (name, kind, lineno), top level functions only
            "imports": [],          # (type, code, lineno), top level imports only
        }

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return results

        for node in tree.body:
            # Top-level imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                kind = "import" if isinstance(node, ast.Import) else "from-import"
                code = ast.unparse(node)
                results["imports"].append((kind, code, node.lineno))

            # Top-level functions
            elif isinstance(node, ast.FunctionDef):
                results["functions"].append((node.name, "def", node.lineno))

            # Top-level classes
            elif isinstance(node, ast.ClassDef):
                class_entry = {
                    "kind": "class",
                    "name": node.name,
                    "line": node.lineno,
                    "functions": [],
                    "imports": []
                }

                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.FunctionDef):
                        class_entry["functions"].append((subnode.name, "def", subnode.lineno))
                    elif isinstance(subnode, (ast.Import, ast.ImportFrom)):
                        kind = "import" if isinstance(subnode, ast.Import) else "from-import"
                        code = ast.unparse(subnode)
                        class_entry["imports"].append((kind, code, subnode.lineno))

                results["classes"].append(class_entry)
    
        return results
    
    @classmethod
    def resolve_import(cls, import_line: str, current_path: str):
        """
        Gets module of import and any class names attached, or "*"
        """
        result = {
            "full_module_path": None,
            "classes_imported": [],
            "as": None,
            "type": "import"
        }

        # Handle relative imports: from ..foo import Bar
        def resolve_relative(module_str: str) -> str:
            if module_str.startswith("."):
                parts = current_path.split(".")
                dots = len(module_str) - len(module_str.lstrip("."))
                rel = module_str.lstrip(".")
                resolved = ".".join(parts[: -dots] + ([rel] if rel else []))
                return resolved
            return module_str

        # Normalize whitespace
        line = import_line.strip()

        # Case 1: from x.y import z or *
        match = re.match(r"from\s+([\w\.]+|(?:\.*[\w\.]*))\s+import\s+(.+)", line)
        if match:
            module_path = match.group(1)
            resolved_mod = resolve_relative(module_path)
            imports = match.group(2).strip()

            result["full_module_path"] = resolved_mod

            if imports == "*":
                result["classes_imported"] = ["*"]
            else:
                class_names = [s.strip().split(" as ")[0] for s in imports.split(",")]
                result["classes_imported"] = class_names

            return result

        # Case 2: import x.y.z [as alias]
        match = re.match(r"import\s+([\w\.]+)(?:\s+as\s+(\w+))?", line)
        if match:
            module_path = match.group(1)
            alias = match.group(2) or module_path.split(".")[-1]

            resolved_mod = resolve_relative(module_path)
            result["full_module_path"] = resolved_mod
            result["alias"] = alias
            return result

        # Case 3. from x.y cimport z
        match = re.match(r"from\s+([\w\.]+|(?:\.*[\w\.]*))\s+cimport\s+(.+)", line)
        if match:
            raw_mod = match.group(1)
            imports = match.group(2).strip()
            resolved_mod = resolve_relative(raw_mod)

            result["full_module_path"] = resolved_mod
            result["type"] = "cimport"

            if imports == "*":
                result["classes_imported"] = ["*"]
            else:
                class_names = [s.strip().split(" as ")[0] for s in imports.split(",")]
                result["classes_imported"] = class_names

            return result

        # Case 4. cimport x.y.z
        match = re.match(r"cimport\s+([\w\.]+)", line)
        if match:
            module_path = match.group(1)
            resolved_mod = resolve_relative(module_path)

            result["full_module_path"] = resolved_mod
            result["type"] = "cimport"
            result["classes_imported"] = None
            result["alias"] = module_path.split(".")[-1]
            return result

        return "ERROR: " + import_line  # not a valid import line

    @classmethod
    def get_full_name(cls, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return cls.get_full_name(node.value) + "." + node.attr
        return None
