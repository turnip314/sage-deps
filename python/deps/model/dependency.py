from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.sageclass import SageClass

class Relation:
    NOTHING = -1
    SUB_METHOD_IMPORT = 0
    TOP_LEVEL_IMPORT = 1
    DECLARED_IMPORT = 2
    CLASS_ATTRIBUTE = 3
    INHERITANCE = 4

class Dependency:
    def __init__(
            self,
            source: 'SageClass',
            target: 'SageClass',
            relation: Relation
    ):
        self.source = source
        self.target = target
        self.relation = relation
