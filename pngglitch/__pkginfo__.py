#!/usr/bin/env python
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

# pylint: disable=invalid-name, redefined-builtin
"""Packaging information for pngglitch."""

name = "pngglitch"
description = "Corrupt PNG files without breaking their checksums"

numversion = (1, 1, 0)
devversion = None

shortversion = "{0[0]}.{0[1]}".format(numversion)
version = ".".join(str(num) for num in numversion)
if devversion is not None:
    version += "-dev" + str(devversion)

author = "Nico Madysa"
copyright = u"2014–2019, Nico Madysa"
author_email = "uebertreiber@gmx.de"
license = "Apache License, Version 2.0"
credits = ["Nico Madysa"]

python_requires = ">=2.7"
entry_points = {
    "console_scripts": [
        "pngglitch = pngglitch.__main__:main",
    ],
}
zip_safe = True
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Other Audience",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 2 :: Only",
    "Topic :: Artistic Software",
]
keywords = "png glitch art"
url = "https://github.com/troiganto/pngglitch"
