from deps.data import Data, Filter
from deps.model.module import Module, File
from deps.model.sageclass import SageClass

import math

class Scorer:
    def run(self):
        pass

class DefaultScorer(Scorer):
    def __init__(self):
        pass

    def score_50_to_top_level_imports(self):
        module: Module
        for module in Data.get_modules_filtered(Filter()):
            if module.full_path_name.endswith("all"):
                if not isinstance(module, File):
                    continue
                for imported_item in module.get_import_map().values():
                    imported_item.set_score(50)
    
    def score_1_for_each_edge(self):
        for sage_class in Data.get_classes_filtered(Filter()):
            sage_class.set_score(
                sage_class.get_score + sage_class.in_degree
                + sage_class.out_degree
            )
    
    def score_commits(self):
        for sage_class in Data.get_classes_filtered(Filter()):
            commit_metadata = Data.get_commit_metadata(sage_class.module.full_path_name)
            commit_score = 0
            if commit_metadata is not None:
                commit_score = commit_metadata['num_commits']//10
                commit_score += commit_metadata['total_adds']//100
                commit_score -= commit_metadata['total_dels']//200
            commit_score //= len(sage_class.module.get_classes())
            commit_score = int(math.sqrt(commit_score))
            sage_class.set_score( 
                sage_class.get_score + commit_score
            )
    
    def set_module_to_max_of_class_score(self):
        module: Module
        for module in Data.get_modules_filtered(Filter()):
            module.set_score(max([0] + [sage_class.get_score for sage_class in module.get_classes()]))

    def run(self):
        """
        If in .all import: +50 score
        For each node (incoming or outgoing) +1 score
        

        Module score = max of child score
        """
        self.score_50_to_top_level_imports()
        self.score_1_for_each_edge()
        self.score_commits()
        self.set_module_to_max_of_class_score()
        
        

        