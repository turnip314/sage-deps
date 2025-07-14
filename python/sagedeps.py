import functools
import json
import threading
import time
import webbrowser
from argparse import ArgumentParser
from http.server import HTTPServer, SimpleHTTPRequestHandler

from analysis import *
from constants import *
from deps.parser import Parser
from deps.loader import Loader
from deps.graphics import create_class_digraph, create_module_digraph, create_graph_json
from deps.score import DefaultScorer
from deps.filter import PathFilter, MinFanIn, MinFanOut, Or, Not, NameContains, Balance, from_json_file
from deps.data import Data

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

def generate_graph(out_file, filter):
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

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:8100/index.html")

if __name__ == "__main__":
    parser = ArgumentParser(prog="sagedeps", description="A program top help manage SageMath dependencies.")
    parser.add_argument("-s", "--sage-source", dest="sage_source", help="The source file of Sage.")
    parser.add_argument("-m", "--modules-source", dest="modules_source",help="Specify the modules file.")
    parser.add_argument("-o", "--output-file", dest="output_file",help="Specify the file to dump the output.")
    parser.add_argument(
        "-up", 
        nargs=2,
        dest="up_dependency",
        help="Generates a breadth-first dependency tree rooted at a particular node, up to a given depth."
    )
    parser.add_argument(
        "-cc", 
        nargs=2,
        dest="check_cycles",
        help="Finds cycles starting at given node."
    )
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
    parser.add_argument(
        "--ff",
        nargs="?",
        dest="filter_source", 
        const=FILTER_JSON,
        default=False,
        help="Load a custom filter. If not, a default filter is used."
    )
    parser.add_argument(
        "-view", "--view",
        dest="show_view",
        action="store_true",
        help="Runs a cytoscape.js instance.")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    
    args = parser.parse_args()

    result = ""

    verbose = args.verbose
    if args.sage_source:
        SAGE_SRC = args.sage_source
    if args.modules_source:
        MODULE_JSON_SRC = args.modules_source
    if args.generate_modules:
        create_module_class_map(args.generate_modules)
    
    Loader.initialize(scorer=DefaultScorer())
    if args.filter_source:
        filter = from_json_file(args.filter_source)
    else:
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
        create_dependencies(args.generate_dependencies)
    if args.generate_imports:
        create_import_map(args.generate_imports)
    if args.generate_graph:
        generate_graph(args.generate_graph, filter)

    if args.show_view:
        threading.Thread(target=open_browser, daemon=True).start()
        run_server()

    if args.output_file:
        with open(Path(__file__).parent/args.output_file, "w+") as f:
            f.write(str(result))
    else:
        print(result)