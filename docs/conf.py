# -*- coding: utf-8 -*-
"""The Sphinx configuration file."""

# pylint: disable=invalid-name

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'pngglitch'
copyright = '2014–2019, Nico Madysa'  # pylint: disable=redefined-builtin
author = 'Nico Madysa'

version = '1.0'
release = '1.0.1'

needs_sphinx = '1.3'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
]
autodoc_member_order = 'groupwise'

templates_path = []
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

default_role = 'py:obj'
manpages_url = 'https://linux.die.net/man/{section}/{page}'

pygments_style = 'sphinx'
html_theme = 'classic'
html_theme_options = {}

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'preamble': '',
    'figure_align': 'htbp',
}
latex_documents = [
    (master_doc, 'pngglitch.tex', 'pngglitch', 'Nico Madysa', 'manual'),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page.
# (source start file, name, description, authors, manual section).
man_pages = [
    ('commandline', 'pngglitch',
     'Add glitch effects to PNG (Portable Network Graphics) files.', [author],
     1),
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'pngglitch', 'pngglitch', author, 'pngglitch',
     'Add glitch effects to PNG (Portable Network Graphics) files.',
     'Miscellaneous'),
]
