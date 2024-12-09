"""
Validation functions for Azure configuration.
"""

from urllib.parse import urlparse


def is_valid_acr_endpoint(endpoint: str) -> tuple[bool, str]:
    """
    Check whether an Azure container
    registry endpoint is valid given
    CFA ACR configurations.

    Parameters
    ----------
    endpoint
        Azure Container Registry endpoint to validate.

    Returns
    -------
    tuple[bool, str]
        First entry: ``True`` if validation passes, else ``False``.
        Second entry: ``None`` if validation passes, else
        a string indicating what failed validation.
    """
    if endpoint.endswith("/"):
        return (
            False,
            (
                "Azure Container Registry URLs "
                "must not end with a trailing "
                "slash, as this can hamper DNS "
                "lookups of the private registry endpoint. "
                f"Got {endpoint}"
            ),
        )

    domain = urlparse(endpoint).netloc

    if not domain.endswith("azurecr.io"):
        return (
            False,
            (
                "Azure Container Registry URLs "
                "must have the domain "
                f"`azurecr.io`. Got `{domain}`."
            ),
        )

    if domain.startswith("azurecr.io"):
        return (
            False,
            (
                "Azure container registry URLs "
                "must have a subdomain, typically "
                "corresponding to the particular "
                "private registry name."
                f"Got {endpoint}"
            ),
        )

    return (True, None)
