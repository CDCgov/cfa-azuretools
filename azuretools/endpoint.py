"""
Helper functions for constructing Azure endpoint URLs.
"""

from urllib.parse import quote, urljoin, urlunparse

import azuretools.defaults as d


def _construct_https_url(netloc: str, path: str = "") -> str:
    """
    Construct a simple https URL via
    :func:`urllib.parse.urlunparse`.

    Parameters
    ----------
    netloc
        ``netloc`` value for :func:`~urllib.parse.urlunparse`
        (subdomains and domain).

    path
        ``path`` value for :func:`~urllib.parse.urlunparse`
        (path after the domain).

    Returns
    -------
    str
        The URL, as a string.
    """
    return urlunparse(
        [
            "https",
            quote(netloc),
            path,
            "",
            "",
            "",
        ]
    )


def construct_batch_endpoint(
    batch_account: str,
    batch_location: str,
    batch_endpoint_subdomain: str = d.default_azure_batch_endpoint_subdomain,
) -> str:
    """
    Construct an Azure Batch endpoint URL from
    the account name, location, and subdomain.

    Parameters
    ----------
    batch_account
        Name of the Azure batch account.

    batch_location
        Location of the Azure batch servers,
        e.g. ``"eastus"``.

    batch_endpoint_subdomain
        Azure batch endpoint subdomains and domains
        that follow the account and location, e.g.
        ``"batch.azure.com/"``, the default.

    Returns
    -------
    str
        The endpoint URL.
    """
    return _construct_https_url(
        f"{batch_account}.{batch_location}.{batch_endpoint_subdomain}"
    )


def construct_azure_container_registry_endpoint(
    azure_container_registry_account: str,
    azure_container_registry_domain: str = d.default_azure_container_registry_domain,
) -> str:
    """
    Construct an Azure container registry endpoint URL
    from the account name, location, and subdomain.

    Parameters
    ----------
    azure_container_registry_account
        Name of the Azure container registry account.

    azure_container_registry_domain
        Domain for the Azure container registry. Typically
        ``"azurecr.io"``, the default.

    Returns
    -------
    str
        The registry endpoint URL.
    """
    return _construct_https_url(
        f"{azure_container_registry_account}.{azure_container_registry_domain}"
    )


def construct_blob_account_endpoint(
    blob_account: str,
    blob_endpoint_subdomain: str = d.default_azure_blob_storage_endpoint_subdomain,
) -> str:
    """
    Construct an Azure blob storage account endpoint URL.

    Parameters
    ----------
    blob_account
        Name of the Azure blob storage account.

    blob_endpoint_subdomain
        Azure batch endpoint subdomains and domains
        that follow the account, e.g.
        ``"blob.core.windows.net/"``, the default.

    Returns
    -------
    str
       The endpoint URL.
    """
    return _construct_https_url(f"{blob_account}.{blob_endpoint_subdomain}")


def construct_blob_container_endpoint(
    blob_container: str,
    blob_account: str,
    blob_endpoint_subdomain: str = d.default_azure_blob_storage_endpoint_subdomain,
) -> str:
    """
    Construct an endpoint URL for a blob storage container
    from the container name, account name, and endpoint subdomain.

    Parameters
    ----------
    blob_container
        Name of the blob storage container.

    blob_account
        Name of the Azure blob storage account.

    blob_endpoint_subdomain
        Azure Blob endpoint subdomains and domains
        that follow the account name, e.g.
        ``"blob.core.windows.net/"``, the default.

    Returns
    -------
    str
       The endpoint URL.
    """
    return urljoin(
        construct_blob_account_endpoint(blob_account, blob_endpoint_subdomain),
        quote(blob_container),
    )
