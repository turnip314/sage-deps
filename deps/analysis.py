from data import Data, Filter
from model.dependency import Dependency, Relation
from model.module import Module, File
from model.sageclass import SageClass

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
 