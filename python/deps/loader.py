import json

from constants import *
from deps.model.dependency import Dependency, Relation
from deps.model.importable import Importable
from deps.model.module import File, Module
from deps.model.sageclass import SageClass, PythonClass, CythonClass
from deps.data import Data


class Loader:
    @classmethod
    def initialize(cls, scorer = None):
        cls.load_all_modules()
        cls.load_all_classes()
        cls.load_all_instantiations()
        cls.build_import_relations()
        cls.create_dependencies()
        cls.load_commit_metadata()
        cls.parse_rst_content()
        if scorer:
            scorer.run()

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

                    symbols = class_dict["symbols"]
                    
                    import_map, file_import_map = sage_class.get_import_map(split_level=True)
                    for alias, imported_class in import_map.items():
                        sage_class.add_dependency(
                            Dependency(
                                source = sage_class,
                                target = imported_class,
                                relation = Relation.SUB_METHOD_IMPORT
                            )
                        )
                        if any([symbol == alias for symbol in symbols]):
                            sage_class.add_dependency(
                            Dependency(
                                source = sage_class,
                                target = imported_class,
                                relation = Relation.DECLARED_SUB_IMPORT
                            )
                        )

                    for alias, imported_class in file_import_map.items():
                        sage_class.add_dependency(
                            Dependency(
                                source = sage_class,
                                target = imported_class,
                                relation = Relation.TOP_LEVEL_IMPORT
                            )
                        )
                        if any([symbol == alias for symbol in symbols]):
                            sage_class.add_dependency(
                            Dependency(
                                source = sage_class,
                                target = imported_class,
                                relation = Relation.DECLARED_TOP_IMPORT
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
        
        sage_class: SageClass
        for sage_class in Data.classes.values():
            sage_class.get_filter_dependencies()

    @classmethod
    def load_commit_metadata(cls):
        def process_path_name(path_name):
            return ".".join(path_name.split(".")[0].split("/")[1:])

        with open(COMMIT_METADATA) as f:
            commit_metadata_raw = json.loads(f.read())
            commit_metadata = {
                process_path_name(key) : value for key, value in commit_metadata_raw.items()
            }

        Data.set_commit_metadata(commit_metadata)

    @classmethod
    def collect_all_rst_files(cls, section_path):
        """
        Recursively collect all .rst files included in this reference section.
        """
        visited = set()
        pending = ["index.rst"]
        all_rst_paths = []

        while pending:
            rel_path = pending.pop()
            rst_path = section_path / rel_path
            if rst_path in visited or not rst_path.exists():
                continue
            visited.add(rst_path)
            all_rst_paths.append(rst_path)

            # Scan for nested toctree includes
            with rst_path.open() as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("..") or line.startswith(":"):
                        continue
                    if not line.endswith(".rst"):
                        line += ".rst"
                    candidate = (section_path / line).resolve()
                    if candidate.exists():
                        pending.append(candidate.relative_to(section_path))

        return all_rst_paths
    
    @classmethod
    def parse_rst_content(cls):
        result = {}
        for section in Path(LOCAL_DOC_ROOT).iterdir():
            index = section / "index.rst"
            if not index.exists():
                continue
            result[section.name] = ""
            rst_files = cls.collect_all_rst_files(section)
            for rst_file in rst_files:
                content = rst_file.read_text()
                result[section.name] += "\n" + content
        
        Data.set_rst_content(result)

    @classmethod
    def get_doc_urls(cls, sage_class: SageClass):
        """
        Given a fully-qualified Sage module path, return a list of documentation URLs
        for each reference section that includes the module.
        """
        matches = []
        module_path = sage_class.module.full_path_name
        html_path = module_path.replace(".", "/") + ".html"
        for reference in Data.get_rst_references(module_path):
            full_url = f"{DOC_BASE_URL}/{reference}/{html_path}#{module_path}"
            matches.append(full_url)

        return matches

    @classmethod
    def dump_import_map(cls, split=False):
        """
        Dumps the currently loaded import map as a dict of the form
        {
            "<sage-full-class-path>": {
                "class-imports": {
                    ...
                },
                "top-level-imports": {
                    ...
                }
            }
        }
        """
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

        
    
