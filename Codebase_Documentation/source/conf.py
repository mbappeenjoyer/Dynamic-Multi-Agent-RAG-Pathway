from unittest import mock
import sys
import os

# List of modules to mock
MOCK_MODULES = [
    'PyPDF2', 'unstructured[all-docs]', 'pillow', 'pydantic', 'lxml', 'matplotlib',
    'unstructured-pytesseract', 'tesseract-ocr', 'llama-index', 'llama-parse',
    'llama-index-core', 'llama-index-postprocessor-flag-embedding-reranker',
    'llama-index-embeddings-huggingface', 'llama-index-embeddings-instructor',
    'llama-index-embeddings-together', 'llama-index-llms-together', 'together',
    'langgraph', 'langchain', 'langchain_experimental', 'langchain-together',
    'langchain_huggingface', 'faiss-gpu', 'datasets', 'accelerate', 'llama-index-packs-raptor',
    'langchain-groq', 'llama-index-llms-groq', 'unstructured-client', 'pymupdf',
    'faiss-cpu', 'pdfplumber', 'sentence-transformers', 'einops', 'llama-index-embeddings-langchain',
    'nmslib', 'llama-index-embeddings-jinaai', 'dotenv'
]

# Mock the modules by updating sys.modules
sys.modules.update((module, mock.Mock()) for module in MOCK_MODULES)

# Project information
project = 'Pathway'
copyright = 'Team 34'
author = ''
release = ''

html_title = "Pathway"

# Path setup
sys.path.insert(0, os.path.abspath('../'))

# Extensions
extensions = [
    "sphinx.ext.autodoc",          # Automatically generate docstrings
    "sphinx.ext.napoleon",         # Support for Google/NumPy style docstrings
    "sphinx_autodoc_typehints",    # Include type hints
    "sphinx.ext.autosummary",      # Create summary tables for modules
    "sphinx.ext.viewcode",         # Add links to source code
]

# Autodoc settings
autoclass_content = 'both'
autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
}

# # Autosummary settings
# autosummary_generate = True

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# General configuration
templates_path = ['_templates']
exclude_patterns = []
source_suffix = '.rst'
master_doc = 'index'

# Suppress specific warnings
suppress_warnings = [
    'autodoc.import_object',
    'autodoc.inherited-members',
]

# HTML output
html_theme = 'furo'
html_static_path = ['_static']

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#1617ED",
        "color-brand-content": "#1617ED",
        "color-api-name": "#0000FF",  # Bright blue for API names (py:method, py:data, py:function)
        "color-api-pre-name": "#0000FF",  # Bright blue for pre-names
        "color-api-keyword": "#0044CC",  # Slightly darker blue for keywords
        # "font-stack--monospace": "Courier New, monospace",
        "font-stack--headings": "Bebas Neue, sans-serif",
        "pygments_style": "livinglogic-light",  # Default for light theme
        "color-link": "#0000FF",  # Set the hyperlink color in light theme
        "color-link-hover": "#0000FF",  # Set the hyperlink hover color in light theme
        "color-link--visited": "#1617ED",
    },
    "dark_css_variables": {
        "color-brand-primary": "#1617ED",
        "color-brand-content": "#1617ED",
        "color-api-name": "#0099FF",  # Bright cyan for API names (py:method, py:data, py:function)
        "color-api-pre-name": "#0099FF",  # Bright cyan for pre-names
        "color-api-keyword": "#66CCFF",  # Lighter blue for keywords
        # "font-stack--monospace": "Courier New, monospace",
        "font-stack--headings": "Bebas Neue, sans-serif",
        "pygments_style": "livinglogic-light",  # Default for light theme
        "color-link--visited": "1617ED",
        "color-link": "#0000FF",  # Set the hyperlink color in light theme
        "color-link-hover": "#0000FF",  # Set the hyperlink hover color in light theme
    },
}