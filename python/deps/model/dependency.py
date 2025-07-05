from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.sageclass import SageClass

class Relation:
    NOTHING = -1
    SUB_METHOD_IMPORT = 0
    TOP_LEVEL_IMPORT = 1
    DECLARED_SUB_IMPORT = 2
    DECLARED_TOP_IMPORT = 3
    CLASS_ATTRIBUTE = 4
    INHERITANCE = 5

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
