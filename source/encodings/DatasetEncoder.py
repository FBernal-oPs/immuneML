# quality: gold

import abc

from source.IO.dataset_export.PickleExporter import PickleExporter
from source.encodings.EncoderParams import EncoderParams


class DatasetEncoder(metaclass=abc.ABCMeta):
    """

    Specification:

        encodings:
            e1: <encoder_class> # encoding without parameters

            e2:
                <encoder_class>: # encoding with parameters
                    parameter: value
    """

    @staticmethod
    @abc.abstractmethod
    def build_object(dataset, **params):
        pass

    @abc.abstractmethod
    def encode(self, dataset, params: EncoderParams):
        pass

    def set_context(self, context: dict):
        return self

    def store(self, encoded_dataset, params: EncoderParams):
        PickleExporter.export(encoded_dataset, params["result_path"])
