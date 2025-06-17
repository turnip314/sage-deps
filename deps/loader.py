import json

from model.module import File, Module
from model.sageclass import SageClass, PythonClass, CythonClass
from data import Data

import json
import os
from dotenv import load_dotenv
from pathlib import Path

class Loader:
    dotenv_path = Path('config.env')
    load_dotenv(dotenv_path=dotenv_path)
    SAGE_SRC = os.getenv("SAGE_SRC")

    @classmethod
    def initialize(cls):
        cls.load_all_modules()

    @classmethod
    def load_all_modules(cls):
        base_module = Module("sage", None)
        Data.add_module("sage", base_module)
        with open("python_cython_modules.json") as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                submodule_names = module_name.split(".")
                parent_module = base_module
                for submodule_name in submodule_names[:-1]:
                    submodule = Data.get_module(
                        parent_module.full_path_name + "." + submodule_name) \
                            or Module(submodule_name, parent_module)
                    Data.add_module(submodule.full_path_name, submodule)
                    parent_module = submodule
                
                file_name = submodule_names[-1]
                file = File(file_name, parent_module, modules_dict[module_name]["extension"])
                Data.add_module(file.full_path_name, file)
    
    @classmethod
    def load_all_classes(cls):
        with open("python_cython_modules.json") as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                classes = modules_dict[module_name]["classes"]
                parent_module = Data.get_module(module_name)
                for classdict in classes:
                    classname = classdict["classname"]
                    sage_class = PythonClass(parent_module, classname)
                    Data.add_class(sage_class.full_path_name, classname, sage_class)

    def build_dependencies(cls):
        pass

    
