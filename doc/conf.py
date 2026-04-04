#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

extensions = [
    "myst_parser",
    "sphinx_rtd_theme",
]

source_suffix = {
    '.md': 'markdown',
    '.rst': 'restructuredtext',
}

html_theme = "sphinx_rtd_theme"

master_doc = 'index'

org_export_settings = {
    'section-numbers': False,
    'todo': True,
    'tags': True,
}

project = "Ymir 1.2"
author = "Emile Cadorel"
copyright = "2021–2026"
version = "1.2"
release = "1.2.0"
