import functools
import json
import threading
import time
import webbrowser
from argparse import ArgumentParser
from http.server import HTTPServer, SimpleHTTPRequestHandler

from sagedeps.analysis import *
from sagedeps.constants import *
from sagedeps.deps.parser import Parser
from sagedeps.deps.loader import Loader
from sagedeps.deps.graphics import create_class_digraph, create_module_digraph, create_graph_json
from sagedeps.deps.score import DefaultScorer
from sagedeps.deps.filter import PathFilter, MinFanIn, MinFanOut, Or, Not, NameContains, Balance, DistanceFilter, from_json_file
from sagedeps.deps.data import Data

httpd = None
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        super().do_GET()
    def do_POST(self):
        if "/closed" in self.path:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Closed received")
            print("Browser was closed or navigated away!")
            threading.Thread(target=httpd.shutdown).start()

def get_default_filter():
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
    return Balance(
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

def generate_graph(out_file=GRAPH_JSON, filter=get_default_filter()):
    result = create_graph_json(
        filter
    )

    with open(out_file, "w") as f:
        f.write(json.dumps(result, indent=4))

def generate_tree(source, distance, direction, out_file=GRAPH_DIR/"tree.json"):
    filter = DistanceFilter(
        source, int(distance), direction
    )
    result = create_graph_json(
        filter
    )

    with open(out_file, "w") as f:
        f.write(json.dumps(result, indent=4))

def run_graph_analysis(analyzer: GraphAnalyzer):
    return analyzer.run()

def run_server():
    global httpd
    handler_class = functools.partial(MyHandler, directory=GRAPH_DIR)
    httpd = HTTPServer(('localhost', 8100), handler_class)
    print("Launching cytoscape viewer...")
    httpd.serve_forever()

def open_browser(file="graph.json"):
    time.sleep(1)
    webbrowser.open(f"http://localhost:8100/index.html?file={file}")

def main():
    global SAGE_SRC
    global MODULE_JSON_SRC
    parser = ArgumentParser(prog="sagedeps", description="A program top help manage SageMath dependencies.")
    parser.add_argument(
        "-s", 
        "--sage-source", 
        metavar="SOURCE_FILE", 
        default=SAGE_SRC, 
        dest="sage_source", 
        help="The source file of Sage."
    )
    parser.add_argument(
        "-m", 
        "--modules-source", 
        metavar="SOURCE_FILE", 
        default=MODULE_JSON_SRC, 
        dest="modules_source",
        help="Specify the modules file."
    )
    parser.add_argument(
        "-g", 
        "--graph-source", 
        metavar="SOURCE_FILE", 
        default=GRAPH_JSON, 
        dest="graph_source",
        help="Specify the graph file."
    )
    parser.add_argument(
        "-o", 
        "--output-file", 
        metavar="OUTPUT_FILE", 
        dest="output_file",
        help="Specify the file to dump the output."
    )
    parser.add_argument(
        "-up", 
        nargs=2,
        metavar=("SOURCE_CLASS", "DEPTH"),
        dest="up_dependency",
        help="Generates a breadth-first dependency tree rooted at SOURCE_CLASS, up to a given depth."
    )
    parser.add_argument(
        "-cc", 
        nargs=2,
        metavar=("SOURCE_CLASS", "TIMEOUT"),
        dest="check_cycles",
        help="Finds cycles starting at SOURCE_CLASS with a timeout of TIMEOUT seconds."
    )
    parser.add_argument(
        "-gm", "--generate-modules",
        action="store_true",
        dest="generate_modules", 
        help="Generate a modules file. Will output to default location or `--modules-source`."
    )
    parser.add_argument(
        "-gi", "--generate-imports",
        action="store_true",
        dest="generate_imports", 
        help="Generate an imports file."
    )
    parser.add_argument(
        "-gd", "--generate-dependencies",
        action="store_true",
        dest="generate_dependencies", 
        help="Generate a dependencies file."
    )
    parser.add_argument(
        "-gg", "--generate-graph",
        action="store_true",
        dest="generate_graph", 
        help="Generate an graph file. Will output to default location or `--graph-source`."
    )
    parser.add_argument(
        "-gdg", "--generate-dependency-graph",
        nargs=3,
        metavar=("SOURCE", "DISTANCE", "DIRECTION"),
        dest="generate_dependency_graph", 
        help="Generate a dependency graph rooted at a SOURCE node."
    )
    parser.add_argument(
        "-f", "--ff",
        dest="filter_source",
        metavar="SOURCE_FILE",
        default=FILTER_JSON,
        help="Load a custom filter. If not, a default filter is used."
    )
    parser.add_argument(
        "-view", "--view",
        action="store_true",
        dest="show_view",
        help="Run a cytoscape.js instance. Specify graph source using `--graph-source`."
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    
    args = parser.parse_args()

    result = ""

    verbose = args.verbose
    SAGE_SRC = args.sage_source
    MODULE_JSON_SRC = args.modules_source
    if args.generate_modules:
        create_module_class_map(args.modules_source)
    
    Loader.initialize(scorer=DefaultScorer())
    try:
        filter = from_json_file(args.filter_source)
    except:
        print("Could not load filter. Using a custom default.")
        filter = get_default_filter()

    if args.up_dependency:
        source = args.up_dependency[0]
        depth = int(args.up_dependency[1])
        result = run_graph_analysis(
            DistanceAnalyzer(source, depth, filter)
        )
    if args.check_cycles:
        source = args.check_cycles[0]
        timeout = int(args.check_cycles[1])
        result = run_graph_analysis(
            CyclesAnalyzer(
            start_node=Data.get_class(source), 
            time_limit = timeout
            )
        )
    if args.generate_dependencies:
        create_dependencies(args.output_file or DEPENDENCIES_JSON)
    if args.generate_imports:
        create_import_map(args.output_file or IMPORT_MAP_SRC)
    if args.generate_graph:
        generate_graph(args.graph_source, filter=filter)
    if args.generate_dependency_graph:
        generate_tree(
            args.generate_dependency_graph[0], 
            args.generate_dependency_graph[1], 
            args.generate_dependency_graph[2],
            args.graph_source or GRAPH_DIR/"dep-graph.json"
        )

    if args.show_view:
        threading.Thread(target=open_browser, daemon=True, args=[args.graph_source]).start()
        run_server()

    if args.output_file:
        with open(Path(__file__).parent/args.output_file, "w+") as f:
            f.write(str(result))
    else:
        print(result)