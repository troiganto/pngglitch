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
"""Setup script for Pngglitch."""

from setuptools import setup

# pylint: disable=invalid-name

long_description = """\
This script offers a class GlitchedPNGFile that enables the user
to partially decompress a PNG file and deliberately put errors into
it's bytestream.

It can also be called from the command line to corrupt PNG files individually
or in bulk.
"""

setup(
    name='pngglitch',
    version='1.0.1',
    python_requires='>=2.7',
    packages=['pngglitch'],
    entry_points={
        'console_scripts': [
            'pngglitch = pngglitch.__main__:main',
        ]
    },
    zip_safe=True,
    author='Nico Madysa',
    author_email='uebertreiber@gmx.de',
    description='Corrupt PNG files without breaking their checksums',
    long_description=long_description,
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Artistic Software',
    ],
    keywords='png glitch art',
    url='https://github.com/troiganto/pngglitch',
)
