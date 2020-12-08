# -*- coding: utf-8 -*-
# Copyright (c) 2020, immuneML Development Team.
# Distributed under the LGPLv2.1+ License. See LICENSE for more info.
"""immune-ML.

This file is part of immne-ML.

immune-ML is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 2.1 of the License, or
(at your option) any later version.

immune-ML is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with immune-ML. If not, see <http://www.gnu.org/licenses/>
"""
import ast
import glob
import pathlib
from codecs import open as openc
from setuptools import setup, find_packages

FULL_VERSION = '0.9.0.dev0'  # Automatically set by setup_version.py


def get_long_description():
    """Return the contents of README.md as a string."""
    here = pathlib.Path(__file__).absolute().parent
    long_description = ''
    with openc(here.joinpath('README.md'), encoding='utf-8') as fileh:
        long_description = fileh.read()
    return long_description


def get_version():
    """Return the version from version.py as a string."""
    here = pathlib.Path(__file__).absolute().parent
    filename = here.joinpath('source', 'version.py')
    with openc(filename, encoding='utf-8') as fileh:
        for lines in fileh:
            if lines.startswith('FULL_VERSION ='):
                version = ast.literal_eval(lines.split('=')[1].strip())
                return version
    return FULL_VERSION


def import_requirements(filename) -> list:
    """Import requirements."""
    with open(filename, 'r') as file:
        requirements = file.read().split("\n")
    return requirements


setup(
    name="immune-ml",
    version=get_version(),
    description="immuneML is a software platform for machine learning analysis of immune receptor sequences",
    long_description=get_long_description(),
    author="Milena Pavlovic",
    author_email="milenpa@student.matnat.uio.no",
    url="https://github.com/uio-bmi/ImmuneML",
    install_requires=import_requirements("requirements.txt"),
    extras_require={
        "R_plots":  import_requirements("requirements_R_plots.txt"),
        "DeepRC":  ["widis-lstm-tools@git+https://github.com/widmi/widis-lstm-tools", "deeprc@git+https://github.com/ml-jku/DeepRC@fec4b4f4b2cd70e00e8de83da169560dec73a419"],
        "TCRDist": import_requirements("requirements_TCRdist.txt"),
    },
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.7',
    packages=find_packages(exclude=["test", "test.*", "performance_tests", "performance_tests.*"]),
    package_data={
        'source': ['IO/dataset_import/conversion/*.csv', "presentation/html/templates/*.html", "presentation/html/templates/css/*.css",
                   "visualization/*.R", "visualization/*.r", 'encodings/atchley_kmer_encoding/*.csv'] +
                  [f"config/default_params/{dir_name.split('/')[-1]}/*.yaml" for dir_name in
                   glob.glob("./source/config/default_params/*")],
        'datasets': [path.rsplit("datasets/")[1] for path in glob.glob("datasets/**/*.tsv", recursive=True)] +
                    [path.rsplit("datasets/")[1] for path in glob.glob("datasets/**/*.csv", recursive=True)]
    },
    entry_points={
        'console_scripts': [
            'immune-ml = source.app.ImmuneMLApp:main'
        ]
    },
)
