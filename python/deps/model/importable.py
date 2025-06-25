from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.module import File
    from deps.model.sageclass import SageClass

class Importable:
    def add_file_import(self, alias: str, file: 'File'):
        pass

    def add_class_import(self, alias: str, sage_class: 'SageClass'):
        pass

    def add_full_import(self, file: 'File'):
        pass
    
    def get_import_map(self) -> dict:
        pass

    @property
    def full_path_name(self) -> str:
        pass

    @property
    def depth(self) -> int:
        pass

    @property
    def in_degree(self) -> int:
        return 0
    
    @property
    def out_degree(self) -> int:
        return 0

    def __hash__(self) -> int:
        return hash(self.full_path_name)