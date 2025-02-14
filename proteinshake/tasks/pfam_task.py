from sklearn import metrics
from functools import cached_property
import numpy as np

from proteinshake.datasets import ProteinFamilyDataset
from proteinshake.tasks import Task

class ProteinFamilyTask(Task):
    """ Predict the protein family classification of a protein structure which groups proteins into evolutionarily-related families. This is a protein-level multi-class prediction.

    .. admonition:: Task Summary 

        * **Input:** one protein
        * **Output:** protein family class (5163 classes) 
        * **Evaluation:** Accuracy (custom task)

    """

    DatasetClass = ProteinFamilyDataset
    
    type = 'Multiclass Classification'
    input = 'Protein'
    output = 'Protein Family (Pfam)'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @property
    def num_classes(self):
        return len(self.token_map)

    @cached_property
    def token_map(self):
        # Pfam': ['Fis1 N-terminal tetratricopeptide repeat (Fis1_TPR_N)', 'Fis1 C-terminal tetratricopeptide repeat (Fis1_TPR_C)'], 
        labels = {p['protein']['Pfam'][0] for p in self.proteins}
        return {label: i for i, label in enumerate(sorted(list(labels)))}

    def dummy_output(self):
        import random
        tokens = list(self.token_map.values())
        return [random.choice(tokens) for _ in range(len(self.test_targets))]

    @property
    def task_in(self):
        return ('protein')

    @property
    def task_type(self):
        return ('protein', 'multi_class')

    @property
    def task_out(self):
        return ('multi_class')

    @property
    def out_dim(self):
        return len(self.token_map)

    @property
    def num_features(self):
        return 20

    def target(self, protein):
        return self.token_map[protein['protein']['Pfam'][0]]

    @property
    def default_metric(self):
        return 'accuracy'

    def evaluate(self, y_true, y_pred):
        """ Using metrics from https://doi.org/10.1073/pnas.1821905116 """
        y_true = np.array(y_true, dtype=int)
        y_pred = np.array(y_pred, dtype=int)
        return {
            'precision': metrics.precision_score(y_true, y_pred, average='macro', zero_division=0),
            'recall': metrics.recall_score(y_true, y_pred, average='macro', zero_division=0),
            'accuracy': metrics.accuracy_score(y_true, y_pred),
            #'AUROC': metrics.roc_auc_score(y_true, y_pred, average='macro', multi_class='ovo'),
        }
