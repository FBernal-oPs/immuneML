import argparse
import yaml
import itertools as it
import os
import sys

from source.encodings.kmer_frequency.ReadsType import ReadsType
from source.encodings.kmer_frequency.sequence_encoding.SequenceEncodingType import SequenceEncodingType
from source.ml_methods.MLMethod import MLMethod
from source.util.PathBuilder import PathBuilder
from source.util.ReflectionHandler import ReflectionHandler


def get_sequence_enc_type(sequence_type, position_type, gap_type):
    if sequence_type == "complete":
        encoding_type = SequenceEncodingType.IDENTITY
    else:
        if position_type == "positional":
            if gap_type == "gapped":
                encoding_type = SequenceEncodingType.IMGT_GAPPED_KMER
            else:
                encoding_type = SequenceEncodingType.IMGT_CONTINUOUS_KMER
        else:
            if gap_type == "gapped":
                encoding_type = SequenceEncodingType.GAPPED_KMER
            else:
                encoding_type = SequenceEncodingType.CONTINUOUS_KMER

    return encoding_type.value


def build_encodings_specs(args):
    encodings = dict()

    for i in range(len(args.sequence_type)):
        enc_name = f"e{i+1}"
        enc_spec = dict()

        enc_spec["sequence_encoding"] = get_sequence_enc_type(args.sequence_type[i],
                                                              None if args.position_type is None else args.position_type[i],
                                                              None if args.gap_type is None else args.gap_type[i])
        enc_spec["reads"] = args.reads[i]

        if args.sequence_type[i] == "subsequence":
            if args.gap_type[i] == "gapped":
                enc_spec["k_left"] = args.k_left[i]
                enc_spec["k_right"] = args.k_right[i]
                enc_spec["min_gap"] = args.min_gap[i]
                enc_spec["max_gap"] = args.max_gap[i]
            else:
                enc_spec["k"] = args.k[i]

        encodings[enc_name] = {"KmerFrequency": enc_spec}

    return encodings


def build_ml_methods_specs(ml_methods):
    return {f"ml{i}": method for i, method in enumerate(ml_methods, start=1)}


def build_settings_specs(enc_names, ml_names):
    return [{"encoding": enc_name, "ml_method": ml_name} for enc_name, ml_name in it.product(enc_names, ml_names)]


def build_specs(args):
    specs = {
        "definitions": {
            "datasets": {
                "d1": {
                    "format": "Pickle",
                    "params": {"path": None}
                }
            },
            "encodings": dict(),
            "ml_methods": dict()
        },
        "instructions": {
            "inst1": {
                "type": "HPOptimization",
                "settings": [],
                "assessment": {
                    "split_strategy": "random",
                    "split_count": None,
                    "training_percentage": None
                },
                "selection": {
                    "split_strategy": "random",
                    "split_count": 1,
                    "training_percentage": 0.7
                },
                "labels": [],
                "dataset": "d1",
                "strategy": "GridSearch",
                "metrics": ["accuracy", "balanced_accuracy"],
                "batch_size": 10,
                "reports": [],
                "optimization_metric": "balanced_accuracy"
            }
        }
    }

    enc_specs = build_encodings_specs(args)
    ml_specs = build_ml_methods_specs(args.ml_methods)
    settings_specs = build_settings_specs(enc_specs.keys(), ml_specs.keys())

    specs["definitions"]["datasets"]["d1"]["params"]["path"] = args.dataset_path
    specs["definitions"]["encodings"] = enc_specs
    specs["definitions"]["ml_methods"] = ml_specs
    specs["instructions"]["inst1"]["settings"] = settings_specs
    specs["instructions"]["inst1"]["assessment"]["split_count"] = args.split_count
    specs["instructions"]["inst1"]["assessment"]["training_percentage"] = args.training_percentage / 100
    specs["instructions"]["inst1"]["labels"] = args.labels

    return specs


def check_arguments(args):
    assert 100 >= args.training_percentage >= 10, "training_percentage must range between 10 and 100"
    assert args.split_count >= 1, "The minimal split_count is 1."

    encoding_err = "When multiple encodings are used, fields must still be of equal length, add 'NA' variables where necessary"
    assert len(args.sequence_type) == len(args.reads), encoding_err
    assert args.position_type is None or len(args.sequence_type) == len(args.position_type), encoding_err
    assert args.gap_type is None or len(args.sequence_type) == len(args.gap_type), encoding_err
    assert args.k is None or len(args.sequence_type) == len(args.k), encoding_err
    assert args.k_left is None or len(args.sequence_type) == len(args.k_left), encoding_err
    assert args.k_right is None or len(args.sequence_type) == len(args.k_right), encoding_err
    assert args.min_gap is None or len(args.sequence_type) == len(args.min_gap), encoding_err
    assert args.max_gap is None or len(args.sequence_type) == len(args.max_gap), encoding_err


def parse_commandline_arguments(args):
    ReflectionHandler.get_classes_by_partial_name("", "ml_methods/")
    ml_method_names = [cl.__name__ for cl in ReflectionHandler.all_nonabstract_subclasses(MLMethod)]

    parser = argparse.ArgumentParser(description="tool for building immuneML Galaxy YAML from arguments")
    parser.add_argument("-o", "--output_path", required=True, help="Output file location (directiory).")
    parser.add_argument("-f", "--file_name", default="specs.yaml", help="Output file name Default name is 'specs.yaml' if not specified.")
    parser.add_argument("-d", "--dataset_path", required=True, help="Path to the pickled dataset file (.iml_dataset extension)")
    parser.add_argument("-l", "--labels", nargs="+", required=True,
                        help="Which metadata labels should be predicted for the dataset.")
    parser.add_argument("-m", "--ml_methods", nargs="+", choices=ml_method_names, required=True,
                        help="Which machine learning methods should be applied.")
    parser.add_argument("-t", "--training_percentage", type=float, required=True,
                        help="The percentage of data used for training.")
    parser.add_argument("-c", "--split_count", type=int, required=True,
                        help="The number of times to repeat the training process with a different random split of the data.")
    parser.add_argument("-s", "--sequence_type", choices=["complete", "subsequence"], required=True, nargs="+",
                        help="Whether complete CDR3 sequences are used, or k-mer subsequences.")
    parser.add_argument("-p", "--position_type", choices=["invariant", "positional"], nargs="+",
                        help="Whether IMGT-positional information is used for k-mers, or the k-mer positions are position-invariant.")
    parser.add_argument("-g", "--gap_type", choices=["gapped", "ungapped"], nargs="+", help="Whether the k-mers contain gaps.")
    parser.add_argument("-k", "--k", type=int, nargs="+", help="K-mer size.")
    parser.add_argument("-kl", "--k_left", type=int, nargs="+", help="Length before gap when k-mers are used.")
    parser.add_argument("-kr", "--k_right", type=int, nargs="+", help="Length after gap when k-mers are used.")
    parser.add_argument("-gi", "--min_gap", type=int, nargs="+", help="Minimal gap length when gapped k-mers are used.")
    parser.add_argument("-ga", "--max_gap", type=int, nargs="+", help="Maximal gap length when gapped k-mers are used.")
    parser.add_argument("-r", "--reads", choices=[ReadsType.UNIQUE.value, ReadsType.ALL.value], nargs="+", required=True,
                        help="Whether k-mer counts should be scaled by unique clonotypes or all observed receptor sequences")

    return parser.parse_args(args)


def main(args):
    parsed_args = parse_commandline_arguments(args)
    check_arguments(parsed_args)
    specs = build_specs(parsed_args)

    PathBuilder.build(parsed_args.output_path)
    output_location = os.path.join(parsed_args.output_path, parsed_args.file_name)

    with open(output_location, "w") as file:
        yaml.dump(specs, file)


if __name__ == "__main__":
    main(sys.argv[1:])