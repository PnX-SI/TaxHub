import sphinx_rtd_theme  # noqa

extensions = ["sphinx_rtd_theme", "myst_parser", "sphinx_contributors"]

source_suffix = [".rst", ".md"]

project = "TaxHub"
html_theme = "sphinx_rtd_theme"
pygments_style = "sphinx"


# These folders are copied to the documentation's HTML output
html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "css/custom.css",
]
