import copy
import os

import pandas as pd

from source.data_model.dataset.Dataset import Dataset
from source.preprocessing.Preprocessor import Preprocessor


class DatasetChainFilter(Preprocessor):

    @staticmethod
    def process(dataset: Dataset, params: dict) -> Dataset:
        processed_dataset = copy.deepcopy(dataset)
        filenames = []
        indices = []
        for index, repertoire in enumerate(dataset.get_data()):
            if all(sequence.metadata.chain == params["keep_chain"] for sequence in repertoire.sequences):
                filename = dataset.get_filenames()[index].replace(os.path.basename(dataset.get_filenames()[index]),
                                                                  "{}.pickle".format(repertoire.identifier))
                os.rename(dataset.get_filenames()[index], filename)
                filenames.append(filename)
                indices.append(index)

        processed_dataset.metadata_file = DatasetChainFilter.build_new_metadata(processed_dataset, indices)
        processed_dataset.set_filenames(filenames)
        return processed_dataset

    @staticmethod
    def build_new_metadata(dataset: Dataset, indices_to_keep: list):
        if dataset.metadata_file:
            df = pd.read_csv(dataset.metadata_file, index_col=0).iloc[indices_to_keep, :]
            path = os.path.dirname(os.path.abspath(dataset.metadata_file)) + "_{}_dataset_chain_filtered.csv" \
                .format(os.path.splitext(os.path.basename(dataset.metadata_file))[0])
            df.to_csv(path)
        else:
            path = None
        return path