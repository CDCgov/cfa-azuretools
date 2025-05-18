# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "AzureTools"
copyright = "2024, Dylan H. Morris"
author = "Dylan H. Morris"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "sphinx.ext.intersphinx", "autoapi.extension"]

templates_path = ["_templates"]
exclude_patterns = []

autoapi_dirs = ["../../azuretools"]

myst_enable_extensions = ["amsmath", "dollarmath"]

add_module_names = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "msrestazure": ("https://msrestazure.readthedocs.io/en/latest/", None),
    "msrest": ("https://msrest.readthedocs.io/en/latest/", None),
    "azure-core": (
        "https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/",
        None,
    ),
    "azure-mgmt-batch": (
        "https://azuresdkdocs.blob.core.windows.net/$web/python/azure-mgmt-batch/latest/",
        None,
    ),
    "azure-mgmt-compute": (
        "https://azuresdkdocs.blob.core.windows.net/$web/python/azure-mgmt-compute/latest/",
        None,
    ),
    "azure-storage-blob": (
        "https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/latest/",
        None,
    ),
    "azure-keyvault": (
        "https://azuresdkdocs.blob.core.windows.net/$web/python/azure-keyvault/latest/",
        None,
    ),
    "azure-batch": (
        "https://azuresdkdocs.blob.core.windows.net/$web/python/azure-batch/latest/",
        None,
    ),
    "azure-identity": (
        "https://azuresdkdocs.blob.core.windows.net/$web/python/azure-identity/latest/",
        None,
    ),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
