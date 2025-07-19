# Standard library imports
from datetime import date

from sphinx.util import logging

# -- Project configuration -----------------------------------------------------

author = "Luciano Barosi"
year = date.today().year

copyright = f"©{year} {author}."

project = "astroUFCG"

# release = version = settings.docs_version() or __version__

# -- Sphinx configuration -----------------------------------------------------

add_module_names = False

exclude_patterns = [
    "content/00_images/*",
    "macros/*",
    "data/",
    "info/",
    "notebooks/*",
    "src/*",
    "info/*",
    "_build/*",
    "_static/*",
    ".vscode/*",
    "README.md",
    ".binder/*",
]

extensions = [
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_favicon",
    "sphinx_multitoc_numbering",
    "sphinx_prolog.infobox",
    "sphinx_prolog.pprolog",
    "sphinx_prolog.solex",
    "sphinx_prolog.swish",
    "sphinx_proof",
    "sphinx-autodoc2",
    "sphinx.ext.autosummary",
    "sphinx.ext.ifconfig",
    "sphinx.ext.imgconverter",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxext.opengraph",
    "myst_parser",
]

# needs_sphinx = "4.3.2"

# -- Extensions configuration --------------------------------------------------

autodoc_member_order = "groupwise"

autodoc_type_aliases = {
    "ArrayLike": "ArrayLike",  # This avoids complicated Unions in generated docs
}

copybutton_prompt_text = ">>> "

intersphinx_mapping = {
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}

napoleon_include_init_with_doc = True


pygments_style = "sphinx"

# suppress some useless and annoying messages from sphinx.ext.viewcode
logging.getLogger("sphinx.ext.viewcode").logger.addFilter(
    lambda rec: not rec.msg.startswith("Didn't find")
)

# -- Options for HTML output ---------------------------------------------------


# html_theme = "pydata_sphinx_theme"
html_theme = "sphinx_book_theme"
templates_path = ["_static/templates"]
html_static_path = ["_static"]

html_css_files = [
    "css/custom.css"  # sem _static/ aqui
]

html_context = {
    "default_mode": "dark",
    # "AUTHOR": author,
    # "DESCRIPTION": "Bokeh visualization library, documentation site.",
    # "SITEMAP_BASE_URL": "https://docs.bokeh.org/en/", # Trailing slash is needed
    # "VERSION": version,
}


html_theme_options = {
    "announcement": "<p class='anuncio'>Verifique o cronograma das aulas!</p>",
    "use_sidenotes": True,
}


html_theme_options = {"footer_start": ["test.html"], "footer_end": ["test.html"]}

favicons = [
    {
        "rel": "icon",
        "sizes": "16x16",
        "href": "================",
    },
]


# --- MYST configuration --------------------------------------------------
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Myst options
# myst_links_externa_newtab = True
myst_number_code_blocks = True
myst_enable_checkboxes = True
