# Standard library imports
import os
import re
from datetime import date

from sphinx.util import logging

# -- Project configuration -----------------------------------------------------

author = "Luciano Barosi"
year = date.today().year

copyright = f"©{year} {author}."

project = "astroUFCG"

#release = version = settings.docs_version() or __version__

# -- Sphinx configuration -----------------------------------------------------

add_module_names = False

exclude_patterns = ["docs/includes/*", "docs/releases/*"]

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
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.ifconfig",
    "sphinx.ext.imgconverter",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxext.opengraph",
]

#needs_sphinx = "4.3.2"

# -- Extensions configuration --------------------------------------------------

autodoc_member_order = "groupwise"

autodoc_type_aliases = {
    "ArrayLike": "ArrayLike",  # This avoids complicated Unions in generated docs
}

copybutton_prompt_text = ">>> "

intersphinx_mapping = {
    "numpy"       : ("https://numpy.org/doc/stable/", None),
    "pandas"      : ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "python"      : ("https://docs.python.org/3/", None),
    "sphinx"      : ("https://www.sphinx-doc.org/en/master/", None),
}

napoleon_include_init_with_doc = True


pygments_style = "sphinx"

# suppress some useless and annoying messages from sphinx.ext.viewcode
logging.getLogger("sphinx.ext.viewcode").logger.addFilter(lambda rec: not rec.msg.startswith("Didn't find"))

# -- Options for HTML output ---------------------------------------------------

html_context = {
    "default_mode": "light",
    # "AUTHOR": author,
    # "DESCRIPTION": "Bokeh visualization library, documentation site.",
    # "SITEMAP_BASE_URL": "https://docs.bokeh.org/en/", # Trailing slash is needed
    # "VERSION": version,
}

# html_css_files = ["custom.css"]

# html_static_path = ["_static"]

html_theme ="pydata_sphinx_theme"

html_theme_options = {
    "external_links": [
        {"name": "UAF",  "url": "https://uaf.ufcg.edu.br"},
    ],
    "github_url": "https://github.com/barosil/astroUFCG",
    "navbar_align": "left",
    "navbar_end": ["navbar-icon-links"],
    "navbar_start": ["navbar-logo", "version-switcher"],
    "pygment_light_style": "xcode",
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "show_nav_level": 2,
    "show_toc_level": 1,
    "switcher": {
        "json_url": json_url,
        "version_match": version_match,
    },
    "use_edit_page_button": False,
    "show_version_warning_banner": True,
    "header_links_before_dropdown": 8,
}

# html_sidebars = {
#     "docs/examples/**": [],
#     "docs/gallery": [],
#     "index": [],
#     "*.rst": ["search-field.html", "sidebar-nav-bs.html"],
#     "dev_guide/**": ["search-field.html", "sidebar-nav-bs.html"],
#     "first_steps/**": ["search-field.html", "sidebar-nav-bs.html"],
#     "reference/**": ["search-field.html", "sidebar-nav-bs.html"],
#     "releases/**": ["search-field.html", "sidebar-nav-bs.html"],
#     "user_guide/**": ["search-field.html", "sidebar-nav-bs.html"],
# }

favicons = [
    {
        "rel": "icon",
        "sizes": "16x16",
        "href": "================",
    },
]

templates_path = ["_templates"]

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