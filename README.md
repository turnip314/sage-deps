# Sage Deps - A Sage Dependency Analysis Tool

This is a ![SageMath](https://www.sagemath.org/) dependency analysis tool used for understanding Sage's structure. It can be used to detect circular imports, upstream dependencies, and provide various dependency-graph metrics including PageRank.

# Installation

To install, simply download or clone the repository. The package requires ![numpy](https://numpy.org/), ![scipy](https://scipy.org/), ![networkx](https://networkx.org/), and ![scikit-network](https://pypi.org/project/scikit-network/).

# Setup and Usage

The package requires access to the ![SageMath repository](https://github.com/sagemath/sage). By default, it assumes you have the repository cloned to the same parent directory as your sage-deps folder. You may modify this by modifying the environment variable `SAGEBASE` in `sagedeps/python/constants.py`, or specifying the Sage installation directory using options (see below).

```
usage: sagedeps [-h] [-s SAGE_SOURCE] [-m MODULES_SOURCE] [-o OUTPUT_FILE] [-up UP_DEPENDENCY UP_DEPENDENCY] [-cc CHECK_CYCLES CHECK_CYCLES] [-gm] [-gi]
                [-gd] [-gg] [-gdg GENERATE_DEPENDENCY_GRAPH GENERATE_DEPENDENCY_GRAPH GENERATE_DEPENDENCY_GRAPH] [--ff [FILTER_SOURCE]]
                [-view [SHOW_VIEW]] [--verbose]

A program top help manage SageMath dependencies.

options:
  -h, --help            show this help message and exit
  -s, --sage-source SAGE_SOURCE
                        The source file of Sage.
  -m, --modules-source MODULES_SOURCE
                        Specify the modules file.
  -o, --output-file OUTPUT_FILE
                        Specify the file to dump the output.
  -up UP_DEPENDENCY UP_DEPENDENCY
                        Generates a breadth-first dependency tree rooted at a particular node, up to a given depth.
  -cc CHECK_CYCLES CHECK_CYCLES
                        Finds cycles starting at given node.
  -gm, --generate-modules
                        Generate a modules file. Can optionally pass in destination file.
  -gi, --generate-imports
                        Generate an imports file. Can optionally pass in destination file.
  -gd, --generate-dependencies
                        Generate a dependencies file. Can optionally pass in destination file.
  -gg, --generate-graph
                        Generate an graph file. Can optionally pass in destination file.
  -gdg, --generate-dependency-graph GENERATE_DEPENDENCY_GRAPH GENERATE_DEPENDENCY_GRAPH GENERATE_DEPENDENCY_GRAPH
                        Generate an tree file.
  --ff [FILTER_SOURCE]  Load a custom filter. If not, a default filter is used.
  -view, --view [SHOW_VIEW]
                        Runs a cytoscape.js instance.
  --verbose             Enable verbose output.
```

# Example Usage

