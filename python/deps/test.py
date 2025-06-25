


def test_load_modules():
    from loader import Loader
    from data import Data
    Loader.load_all_modules()
    for module in Data.modules.values():
        print(module.full_path_name)

def test_cython_parse():
    from loader import Loader
    result = Loader.parse_cython("/Users/turnip/Documents/CS 646 Research/sage/src/sage/rings/real_arb.pyx")
    for cname, kind, lineno in result["classes"]:
        print(f"CLASS:    {kind} {cname} @ line {lineno}")

    for fname, kind, lineno in result["functions"]:
        print(f"FUNCTION: {kind} {fname} @ line {lineno}")

    for kind, code, lineno in result["imports"]:
        print(f"IMPORT:   {kind} @ line {lineno}: {code}")

test_cython_parse()