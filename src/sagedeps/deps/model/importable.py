from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sagedeps.deps.model.dependency import Relation
    from sagedeps.deps.model.module import File
    from sagedeps.deps.model.sageclass import SageClass

    from typing import List

class Importable:
    def add_file_import(self, alias: str, file: 'File'):
        raise NotImplementedError(f"{self.__class__.__name__} is an abstract base class.")

    def add_class_import(self, alias: str, sage_class: 'SageClass'):
        raise NotImplementedError(f"{self.__class__.__name__} is an abstract base class.")

    def add_full_import(self, file: 'File'):
        raise NotImplementedError(f"{self.__class__.__name__} is an abstract base class.")
    
    def get_import_map(self) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__} is an abstract base class.")

    @property
    def full_path_name(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} is an abstract base class.")

    @property
    def depth(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__} is an abstract base class.")

    def in_degree(self, relations: 'List[Relation] | None' = None) -> int:
        raise NotImplementedError(f"{self.__class__.__name__} is an abstract base class.")
    
    def out_degree(self, relations: 'List[Relation] | None' = None) -> int:
        raise NotImplementedError(f"{self.__class__.__name__} is an abstract base class.")
    
    @property
    def get_score(self) -> int:
        return self._score
    
    def set_score(self, score: int):
        self._score = score

    def __hash__(self) -> int:
        return hash(self.full_path_name)