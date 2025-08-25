"""
Test the blob module from AzureTools.
"""

from contextlib import nullcontext

import pytest

import azuretools.blob as blob
from azuretools.util import ensure_listlike


def does_not_raise(*args, **kwargs):
    """
    No error context with arbitrary
    args and kwargs
    """
    return nullcontext()


@pytest.mark.parametrize(
    [
        "storage_containers",
        "account_names",
        "identity_references",
        "mount_names",
        "expectation_context",
        "expectation_err",
        "expectation_regex",
    ],
    [
        [
            ["a", "b", "c"],
            ["one", "two"],
            "q",
            None,
            pytest.raises,
            ValueError,
            (
                "{n_account_names} `account_names` and "
                "{n_containers} `storage_containers`."
            ),
        ],
        [
            "a",
            "b",
            "q",
            ["w", "x", "y", "z"],
            pytest.raises,
            ValueError,
            ("{n_mount_names} `mount_names` and {n_containers} `storage_containers`."),
        ],
        [
            ["a", "b", "c"],
            ["one", "two", "three"],
            ["p", "q"],
            None,
            pytest.raises,
            ValueError,
            (
                "{n_identity_refs} `identity_references` and "
                "{n_containers} `storage_containers`."
            ),
        ],
        [
            ["a", "b", "c"],
            ["one", "two", "three"],
            ["p", "q", "r"],
            None,
            does_not_raise,
            None,
            "",
        ],
        [["a", "b", "c", "d"], "one", "p", None, does_not_raise, None, ""],
        [
            ["a", "b", "c", "d"],
            "one",
            "p",
            ["q__", "r__", "s__", "t__"],
            does_not_raise,
            None,
            "",
        ],
    ],
)
def test_get_node_mount_config_errors(
    storage_containers,
    account_names,
    identity_references,
    mount_names,
    expectation_context,
    expectation_err,
    expectation_regex,
):
    """
    Test that :func:`blob.get_node_mount_config`
    errors when appropriate.
    """
    count_vars = dict(
        n_containers=len(ensure_listlike(storage_containers)),
        n_account_names=len(ensure_listlike(account_names)),
        n_mount_names=len(ensure_listlike(mount_names)),
        n_identity_refs=len(ensure_listlike(identity_references)),
    )
    with expectation_context(
        expectation_err, match=expectation_regex.format(**count_vars)
    ):
        blob.get_node_mount_config(
            storage_containers,
            account_names,
            identity_references,
            mount_names=mount_names,
        )
