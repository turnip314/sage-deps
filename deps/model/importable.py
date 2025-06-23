from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.module import File
    from model.sageclass import SageClass

class Importable:
    def add_file_import(self, alias: str, file: 'File'):
        pass

    def add_class_import(self, alias: str, sage_class: 'SageClass'):
        pass

    def add_full_import(self, file: 'File'):
        pass
    
    def get_import_map(self):
        pass

    @property
    def full_path_name(self) -> str:
        pass

    @property
    def depth(self) -> int:
        pass

    def __hash__(self) -> int:
        return hash(self.full_path_name)