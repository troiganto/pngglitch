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

pygments_style = 'sphinx'
html_theme = 'classic'
html_theme_options = {}
# html_static_path = []

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

htmlhelp_basename = 'pngglitchdoc'
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'preamble': '',
    'figure_align': 'htbp',
}
latex_documents = [
    (master_doc, 'pngglitch.tex', 'pngglitch', 'Nico Madysa', 'manual'),
]
man_pages = [(master_doc, 'pngglitch', 'pngglitch Documentation', [author], 1)]
texinfo_documents = [
    (master_doc, 'pngglitch', 'pngglitch', author, 'pngglitch',
     'Add glitch effects to PNG files.', 'Miscellaneous'),
]
