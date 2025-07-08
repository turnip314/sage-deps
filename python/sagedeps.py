import json
from argparse import ArgumentParser
from typing import Type

from analysis import *
from constants import *
from deps.model.dependency import Relation
from deps.model.module import File, Module
from deps.parser import Parser
from deps.loader import Loader
from deps.data import Data
from deps.graphics import create_class_digraph, create_module_digraph, create_graph_json
from deps.score import DefaultScorer
from deps.filter import PathFilter, MinFanIn, MinFanOut, Or, Not, NameContains, ScoreFilter, Balance, Filter

def create_module_class_map(out_file, testing=False):
    class_map = Parser.create_python_module_class_map(list_symbols=not testing)
    class_map_json = json.dumps(class_map, indent=4)
    with open(out_file, "w+") as f: 
        f.write(class_map_json)

def create_import_map(out_file):
    import_map = Loader.dump_import_map(split=True)
    with open(out_file, "w+") as f: 
        f.write(json.dumps(import_map, indent=4))

def create_dependencies(out_file):
    dependencies_map = Loader.dump_dependencies()
    dependencies_map_json = json.dumps(dependencies_map, indent=4)
    with open(out_file, "w+") as f:
        f.write(dependencies_map_json)
    
def show_module_graph(depth=3, path="sage"):
    create_module_digraph(depth=depth, path=path)

def generate_graph(out_file):
    general_filter = Or(
        MinFanOut(1),
        MinFanIn(1)
    ).add(
        Not(
            NameContains("toy"),
            NameContains("example"),
            NameContains("lazy_import"),
            NameContains("test")
        )
    )

    result = create_graph_json(
        Balance(
            lambda x: x.get_score,
            500,
            None,
            PathFilter("sage.rings").add(general_filter),
            PathFilter("sage.combinat").add(general_filter),
            Not(
                PathFilter("sage.rings").add(general_filter),
                PathFilter("sage.combinat").add(general_filter),
            )
        )
    )

    with open(out_file, "w") as f:
        f.write(json.dumps(result, indent=4))

def run_graph_analysis(analyzer: GraphAnalyzer):
    print(analyzer.run())

if __name__ == "__main__":
    parser = ArgumentParser(prog="sagedeps", description="A program top help manage SageMath dependencies.")
    parser.add_argument("-s", "--sage-source", dest="sage_source", help="The source file of Sage.")
    parser.add_argument("-m", "--modules-source", dest="modules_source",help="Specify the modules file.")
    parser.add_argument(
        "--gm", "--generate-modules",
        nargs="?",
        const=MODULE_JSON_SRC,
        default=False,
        dest="generate_modules", 
        help="Generate a modules file. Can optionally pass in destination file."
    )
    parser.add_argument(
        "--gi", "--generate-imports",
        nargs="?",
        const=IMPORT_MAP_SRC,
        default=False,
        dest="generate_imports", 
        help="Generate an imports file. Can optionally pass in destination file."
    )
    parser.add_argument(
        "--gd", "--generate-dependencies",
        nargs="?",
        const=DEPENDENCIES_JSON,
        default=False,
        dest="generate_dependencies", 
        help="Generate a dependencies file. Can optionally pass in destination file."
    )
    parser.add_argument(
        "--gg", "--generate-graph",
        nargs="?",
        const=GRAPH_JSON,
        default=False,
        dest="generate_graph", 
        help="Generate an graph file. Can optionally pass in destination file."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")

    args = parser.parse_args()

    verbose = args.verbose
    if args.sage_source:
        SAGE_SRC = args.sage_source
    if args.modules_source:
        MODULE_JSON_SRC = args.modules_source
    if args.generate_modules:
        create_module_class_map(args.generate_modules)
    
    Loader.initialize(scorer=DefaultScorer())
    if args.generate_dependencies:
        create_dependencies(args.generate_dependencies)
    if args.generate_imports:
        create_import_map(args.generate_imports)
    if args.generate_graph:
        create_import_map(args.generate_graph)

