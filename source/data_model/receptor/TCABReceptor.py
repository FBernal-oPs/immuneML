from source.data_model.receptor.Receptor import Receptor
from source.data_model.receptor.receptor_sequence.ReceptorSequence import ReceptorSequence


class TCABReceptor(Receptor):

    def __init__(self, alpha: ReceptorSequence = None, beta: ReceptorSequence = None, metadata: dict = None, identifier: str = None):

        self.alpha = alpha
        self.beta = beta
        self.metadata = metadata
        self.identifier = identifier

    def get_chains(self):
        return ["alpha", "beta"]
