"""
Test the validate module from
AzureTools.
"""

from contextlib import nullcontext as does_not_raise

import pytest

from azuretools import validate as v
from azuretools.auth import CredentialHandler


@pytest.mark.parametrize(
    ["endpoint", "expected_bool", "expected_message_snippet"],
    [
        ["https://test.azurecr.io", True, None],
        ["https://test.azurecr.io/", False, "trailing slash"],
        ["https://azurecr.io", False, "subdomain"],
        ["https://test.example.com", False, "azurecr"],
    ],
)
def test_is_valid_acr_endpoint(
    endpoint, expected_bool, expected_message_snippet
):
    result_bool, result_msg = v.is_valid_acr_endpoint(endpoint)
    assert result_bool is expected_bool
    if expected_message_snippet is None:
        assert result_msg is None
    else:
        assert expected_message_snippet in result_msg


@pytest.mark.parametrize(
    ["acr_account", "acr_domain", "context"],
    [
        [
            "test",
            "azurecr.io/",
            pytest.raises(ValueError, match="trailing slash"),
        ],
        [
            "test",
            "azurecr.io",
            does_not_raise(),
        ],
        ["test", "example.com", pytest.raises(ValueError, match="azurecr.io")],
    ],
)
def test_cred_handler_uses_acr_endpoint_validation(
    acr_account, acr_domain, context
):
    creds = CredentialHandler(
        azure_container_registry_account=acr_account,
        azure_container_registry_domain=acr_domain,
        azure_user_assigned_identity="",
    )
    with context:
        creds.azure_container_registry
