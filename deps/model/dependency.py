from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.sageclass import SageClass

class Relation:
    NOTHING = -1
    SUB_METHOD_IMPORT = 0
    TOP_LEVEL_IMPORT = 1
    CLASS_ATTRIBUTE = 2
    INHERITANCE = 3

class Dependency:
    def __init__(
            self,
            target: 'SageClass',
            relation: Relation
    ):
        self.target = target
        self.relation = relation
