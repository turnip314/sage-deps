import json

from constants import *
from deps.model.dependency import Dependency, Relation
from deps.model.importable import Importable
from deps.model.module import File, Module
from deps.model.sageclass import SageClass, PythonClass, CythonClass
from deps.data import Data


class Loader:
    @classmethod
    def initialize(cls):
        cls.load_all_modules()
        cls.load_all_classes()
        cls.load_all_instantiations()
        cls.build_import_relations()
        cls.create_dependencies()

    @classmethod
    def load_all_modules(cls):
        """Creates `Module` objects for every module found in `python_cython_modules.json`.
        Loads in their name and path, but no other info
        """
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
        """
        Creates `SageClass` objects for every class found in `python_cython_modules.json`.
        Loads in their name, path, and parent module.
        """
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
    def load_all_instantiations(cls):
        with open(MODULE_JSON_SRC) as f:
            modules_dict = json.loads(f.read())
            for module_name in modules_dict.keys():
                instantiations = modules_dict[module_name]["instantiations"]
                for instantiation in instantiations:
                    full_path_name = module_name + "." + instantiation["name"]
                    referenced_name = module_name + "." + instantiation["func_name"]
                    if instantiation["type"] == "alias":
                        Data.add_alias(full_path_name, referenced_name)
                    else:
                        Data.add_instantiation(full_path_name, referenced_name)

    @classmethod
    def build_import_relations(cls):
        """
        Creates import maps for every `Importable` objects. This includes
        `Module` and `SageClass` objects.

        For `from` imports, we obtain all classes imported this way and add
        to the `Importable` as a key-value pair `alias`:`Importable`, where
        `alias` is how the class will be referenced inside the particular
        class or file.

        For `import` or `cimport`, the `alias` is given by `filename_alias`.
        Classes have the alias `filename_alias.classname` - though this is
        computed recursively within the `Importable`'s own `get_import_map`
        method. Otherwise, it will only store `from` imports and explicit
        imports.
        """
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
        """
        Subroutine called by `build_import_dependencies` that checks if an import
        statement is a `from` import or regular import, and updates the `Importable`
        as a class or file import respectively.
        """
        for import_dict in import_dicts:
            imported_module = Data.get_module(import_dict["full_module_path"])
            if imported_module is not None and isinstance(imported_module, File):
                if import_dict["type"] in ["from-import", "from-cimport", "lazy-import"]:
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
    def create_dependencies(cls):
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
                    
                    import_map, file_import_map = sage_class.get_import_map(split_level=True)
                    for imported_class in import_map.values():
                        sage_class.add_dependency(
                            Dependency(
                                source = sage_class,
                                target = imported_class,
                                relation = Relation.SUB_METHOD_IMPORT
                            )
                        )
                    
                    for imported_class in file_import_map.values():
                        sage_class.add_dependency(
                            Dependency(
                                source = sage_class,
                                target = imported_class,
                                relation = Relation.TOP_LEVEL_IMPORT
                            )
                        )
                    
                    full_import_map = import_map
                    full_import_map.update(file_import_map)
                    for inherited_class_name in class_dict["inherited"]:
                        inherited_class = full_import_map.get(inherited_class_name)
                        if inherited_class is not None:
                            sage_class.add_dependency(
                                Dependency(
                                    source = sage_class,
                                    target = inherited_class,
                                    relation = Relation.INHERITANCE
                                )
                            )
                    
                    for attribute_name in class_dict["attributes"]:
                        attribute_class = full_import_map.get(attribute_name)
                        if attribute_class is not None:
                            sage_class.add_dependency(
                                Dependency(
                                    source = sage_class,
                                    target = attribute_class,
                                    relation = Relation.CLASS_ATTRIBUTE
                                )
                            )
        
        for sage_class in Data.classes.values():
            sage_class.filter_dependencies()

    
    @classmethod
    def dump_import_map(cls, split=False):
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

                    if split:
                        sub_import_map, top_import_map = sage_class.get_import_map(split_level=True)
                        sub_import_map = {key:value.full_path_name for key, value in sub_import_map.items()}
                        top_import_map = {key:value.full_path_name for key, value in top_import_map.items()}
                        result[full_class_path] = {
                            "class-imports": sub_import_map,
                            "top-level-imports": top_import_map
                        }
                    else:
                        import_map = {key:value.full_path_name for key, value in sage_class.get_import_map().items()}
                        result[full_class_path] = import_map
        
        return result
    
    @classmethod
    def dump_dependencies(cls):
        result = {}
        sage_class: SageClass
        for path, sage_class in Data.classes.items():
            result[path] = sage_class.to_dict()["dependencies"]
        
        return result

        
    
