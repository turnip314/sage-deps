import json

from constants import *
from model.importable import Importable
from model.module import File, Module
from model.sageclass import SageClass, PythonClass, CythonClass
from data import Data


class Loader:
    @classmethod
    def initialize(cls):
        cls.load_all_modules()
        cls.load_all_classes()
        cls.build_import_relations()

    @classmethod
    def load_all_modules(cls):
        base_module = Module("sage", None)
        Data.add_module("sage", base_module)
        with open(MODULE_JSON_SRC) as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                submodule_names = module_name.split(".")[1:]
                parent_module = base_module
                for submodule_name in submodule_names[:-1]:
                    submodule = Data.get_module(
                        parent_module.full_path_name + "." + submodule_name)
                    if submodule is None:
                        submodule = Module(submodule_name, parent_module)
                        parent_module.add_child(submodule)
                    Data.add_module(submodule.full_path_name, submodule)
                    parent_module = submodule
                
                file_name = submodule_names[-1]
                file = File(file_name, parent_module, modules_dict[module_name]["extension"])
                parent_module.add_child(file)
                Data.add_module(file.full_path_name, file)
    
    @classmethod
    def load_all_classes(cls):
        with open(MODULE_JSON_SRC) as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                py_cls = PythonClass if modules_dict[module_name]["extension"] == ".py" else CythonClass
                classes = modules_dict[module_name]["classes"]
                parent_module = Data.get_module(module_name)
                if parent_module is None or not isinstance(parent_module, File):
                    print(f"Parent module {module_name} not found")
                    continue
                for classdict in classes:
                    classname = classdict["classname"]
                    sage_class = py_cls(parent_module, classname)
                    parent_module.add_class(sage_class)
                    Data.add_class(sage_class.full_path_name, sage_class)

    @classmethod
    def build_import_relations(cls):
        with open(MODULE_JSON_SRC) as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                module = Data.get_module(module_name)
                if module is None or not isinstance(module, File):
                    print(f"Cannot find module {module_name}")
                    continue

                module_dict = modules_dict[module_name]
                top_level_imports = module_dict["imports"]
                cls.add_imports(module, top_level_imports)

                defined_classes = module_dict["classes"]
                for class_dict in defined_classes:
                    full_class_path = module_name + "." + class_dict["classname"]
                    sage_class = Data.get_class(full_class_path)
                    if sage_class is None or not isinstance(sage_class, SageClass):
                        print(f"Cannot find class {full_class_path}")
                        continue
                    class_level_imports = class_dict["imports"]
                    cls.add_imports(sage_class, class_level_imports)

    @classmethod
    def add_imports(cls, object: Importable, import_dicts: dict):
        for import_dict in import_dicts:
            imported_module = Data.get_module(import_dict["full_module_path"])
            if imported_module is not None and isinstance(imported_module, File):
                if import_dict["type"] == "from-import":
                    if import_dict["classes_imported"] == "*":
                        object.add_full_import(imported_module)
                        continue
                    for alias, classname in import_dict["classes_imported"].items():
                        full_class_path = import_dict["full_module_path"] + "." + classname
                        imported_class = Data.get_class(full_class_path)
                        if imported_class is not None and isinstance(imported_class, SageClass):
                            object.add_class_import(alias, imported_class)
                else:
                    object.add_file_import(import_dict["alias"], imported_module)
    
    @classmethod
    def dump_import_map(cls):
        result = {}
        with open(MODULE_JSON_SRC) as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                module = Data.get_module(module_name)
                if module is None or not isinstance(module, File):
                    print(f"Cannot find module {module_name}")
                    continue
                module_dict = modules_dict[module_name]
                defined_classes = module_dict["classes"]
                for class_dict in defined_classes:
                    full_class_path = module_name + "." + class_dict["classname"]
                    sage_class = Data.get_class(full_class_path)
                    if sage_class is None or not isinstance(sage_class, SageClass):
                        print(f"Cannot find class {full_class_path}")
                        continue
                    import_map = {key:value.full_path_name for key, value in sage_class.get_import_map().items()}
                    result[full_class_path] = import_map
        
        return result

    @classmethod
    def build_dependencies(cls):
        with open(MODULE_JSON_SRC) as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                module = Data.get_module(module_name)
                if module is None or not isinstance(module, File):
                    print(f"Cannot find module {module_name}")
                    continue

                module_dict = modules_dict[module_name]

                defined_classes = module_dict["classes"]
                for class_dict in defined_classes:
                    full_class_path = module_name + "." + class_dict["classname"]
                    sage_class = Data.get_class(full_class_path)
                    if sage_class is None or not isinstance(sage_class, SageClass):
                        print(f"Cannot find class {full_class_path}")
    
