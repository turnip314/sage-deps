from typing import List

from sagedeps.deps.data import Data
from sagedeps.deps.filter import Filter, PathFilter, MinDepthFilter
from sagedeps.deps.model.dependency import Dependency, Relation
from sagedeps.deps.model.module import Module, File
from sagedeps.deps.model.sageclass import SageClass
from sagedeps.deps.loader import Loader

import json
import networkx as nx
import random

def random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

def relation_to_colour(relation: Relation):
    return {
        Relation.DECLARED_SUB_IMPORT: "yellow",
        Relation.DECLARED_TOP_IMPORT: "lime",
        Relation.CLASS_ATTRIBUTE: "cyan",
        Relation.INHERITANCE: "purple"
    }[relation]

def create_class_digraph():
    G = nx.DiGraph()
    classes = Data.get_classes_filtered(PathFilter())
    
    sage_class: SageClass
    for sage_class in classes:
        G.add_node(hash(sage_class))

    for sage_class in classes:
        for dep in sage_class.get_dependencies():
            G.add_edge(
                hash(sage_class),
                hash(dep.target), 
                #relation = dep.relation, 
                #color = relation_to_colour(dep.relation)
            )
    
    return G

def create_module_digraph(filter: Filter, relations: List[Relation]):
    G = nx.DiGraph()
    modules = Data.get_modules_filtered(filter)
    print(f"Number of modules: {len(modules)}")
    
    module: Module
    for module in modules:
        path = module.parent.full_path_name if module.parent is not None else ""
        G.add_node(
            hash(module),
            label=module.full_path_name.removeprefix(path),
            color=random_color()
        )

    for module in modules:
        for other in modules:
            if module == other:
                continue
            if module.depends_on(other, relations=relations):
                G.add_edge(hash(module), hash(other))
    
    return G

def create_graph_json(
    filter: Filter
):
    result = {
        "elements": {
            "nodes": [],
            "edges": []
        }
    }

    classes = Data.get_classes_filtered(filter)
    modules = Data.get_modules_filtered(filter)
    modules = [m for m in modules if any(c in m.get_classes() for c in classes)]
    print(len(classes))
    print(len(modules))

    module: Module
    for module in modules:
        data = {
            "id": module.full_path_name,
            "label": module.name,
            "type": "file" if isinstance(module, File) else "module",
            "score": module.get_score
        }
        if module.parent is not None and module.parent in modules:
            data["parent"] = module.parent.full_path_name
        result["elements"]["nodes"].append({
            "data": data,
            "classes": data["type"]
        })

    sage_class: SageClass
    for sage_class in classes:
        data = {
            "id": sage_class.full_path_name,
            "label": sage_class.name,
            "type": "class",
            "score": sage_class.get_score
        }
        if sage_class.module in modules:
            data["parent"] = sage_class.module.full_path_name
        
        data["urls"] = Loader.get_doc_urls(sage_class)

        result["elements"]["nodes"].append(
            {
                "data": data,
                "classes": "class"
            }
        )

        dep: Dependency
        for dep in sage_class.get_dependencies():
            if dep.target == sage_class or dep.target not in classes:
                continue
            result["elements"]["edges"].append(
                {
                    "data": {
                        "id": f"{sage_class.full_path_name}-{dep.target.full_path_name}",
                        "source": sage_class.full_path_name,
                        "target": dep.target.full_path_name,
                        "type": dep.relation
                    } 
                }
            )
    return result
 