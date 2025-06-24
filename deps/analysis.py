from constants import *
from data import Data, Filter
from model.dependency import Dependency, Relation
from model.module import Module, File
from model.sageclass import SageClass

import json
import networkx as nx
import random

def random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

def relation_to_colour(relation: Relation):
    return {
        Relation.SUB_METHOD_IMPORT: "yellow",
        Relation.TOP_LEVEL_IMPORT: "lime",
        Relation.CLASS_ATTRIBUTE: "cyan",
        Relation.INHERITANCE: "purple"
    }[relation]

def create_class_digraph():
    G = nx.DiGraph()
    classes = Data.get_classes_filtered(Filter().in_path("sage.rings"))
    
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

def create_module_digraph(depth=3, path="sage", relations=None):
    G = nx.DiGraph()
    modules = Data.get_modules_filtered(Filter().depth(depth).in_path(path))
    print(f"Number of modules: {len(modules)}")
    
    module: Module
    for module in modules:
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

def default_score(sage_class: SageClass):
    return sage_class.in_degree + sage_class.out_degree

def create_graph_json(
        depth = None,
        min_depth = None,
        max_depth = None,
        path = "sage",
        min_in = 0,
        min_out = 0,
        excludes = []
):
    result = {
        "elements": {
            "nodes": [],
            "edges": []
        }
    }
    filter = Filter().depth(depth).in_path(path) \
        .min_in(min_in).min_out(min_out).min_depth(min_depth)\
        .max_depth(max_depth)
    
    for word in excludes:
        filter = filter.not_contains(word)

    classes = Data.get_classes_filtered(filter)
    modules = Data.get_modules_filtered(filter)
    print(len(classes))
    print(len(modules))

    module: Module
    for module in modules:
        data = {
            "id": module.full_path_name,
            "label": module.full_path_name,
            "type": "file" if isinstance(module, File) else "module",
            "score": 100
        }
        if module.parent is not None:
            data["parent"] = module.parent.full_path_name
        
        result["elements"]["nodes"].append({
            "data": data,
            "classes": data["type"]
        })

    sage_class: SageClass
    for sage_class in classes:
        result["elements"]["nodes"].append(
            {
                "data": {
                    "id": sage_class.full_path_name,
                    "label": sage_class.full_path_name,
                    "type": "class",
                    "parent":sage_class.module.full_path_name,
                    "score": default_score(sage_class)
                },
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
        
    with open(GRAPH_JSON, "w") as f:
        f.write(json.dumps(result, indent=4))
 