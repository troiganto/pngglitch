#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2014–2019 Nico Madysa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=invalid-name, exec-used
"""Setup script for pngglitch."""

import os
import sys
from setuptools import setup
try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {"build_sphinx": BuildDoc}
except ImportError:
    print >> sys.stderr, "info: install Sphinx to build documentation"

__docformat__ = "restructuredtext en"

# Source information from __pkginfo__.py.
basedir = os.path.dirname(__file__)
__pkginfo__ = {}
with open(os.path.join(basedir, "pngglitch", "__pkginfo__.py")) as infile:
    exec infile.read() in __pkginfo__

# Source long description from README.rst.
with open(os.path.join(basedir, "README.rst")) as infile:
    long_description = infile.read()

setup(
    name=__pkginfo__["name"],
    version=__pkginfo__["version"],
    python_requires=__pkginfo__["python_requires"],
    packages=["pngglitch"],
    entry_points=__pkginfo__["entry_points"],
    zip_safe=__pkginfo__["zip_safe"],
    author=__pkginfo__["author"],
    author_email=__pkginfo__["author_email"],
    description=__pkginfo__["description"],
    long_description=long_description,
    license=__pkginfo__["license"],
    classifiers=__pkginfo__["classifiers"],
    keywords=__pkginfo__["keywords"],
    url=__pkginfo__["url"],
    command_options={
        "build_sphinx": {
            "project": ("setup.py", __pkginfo__["name"]),
            "version": ("setup.py", __pkginfo__["shortversion"]),
            "release": ("setup.py", __pkginfo__["version"]),
            "copyright": ("setup.py", __pkginfo__["copyright"]),
            "source_dir": ("setup.py", "docs"),
            "builder": ("setup.py", ["html", "man"]),
        },
    },
)
