"""
Tests for the config module
"""

import os
from unittest import mock

import pytest

import azuretools.config as config


def test_get_var_errors():
    with mock.patch.dict(
        os.environ, {"VAR_ONE": "val1", "VAR_TWO": "val2"}, clear=True
    ):
        with pytest.raises(ValueError, match="Must either provide"):
            config.get_config_val("VAR_ONE", try_env=False)
        with pytest.raises(
            ValueError,
            match=(
                "(?=.*value for 'variable three')"
                "(?=.*environment variable named "
                "'VAR_THREE')"
            ),
        ):
            config.get_config_val("vAR_three", value_name="variable three")
        with pytest.raises(ValueError, match="Also searched"):
            config.get_config_val("var_three", config_dict={"var_two": "val2"})
        with pytest.raises(
            ValueError,
            match=("(?=.*value for 'variable two')(?=.*under the key 'var_two')"),
        ):
            config.get_config_val(
                "var_two",
                config_dict={"var_one": "val_one"},
                try_env=False,
                value_name="variable two",
            )


def test_get_config_precedence():
    """
    Confirm that the config dict takes
    precedence over the environment variables
    when there is a match in both, but that
    we successfully fall back on the environment
    variable when there is no match in the config_dict.
    """
    mock_env_vars = {"VAR_ONE": "val1", "VAR_TWO": "val2"}
    config_dict = {"var_one": "a val"}
    with mock.patch.dict(os.environ, mock_env_vars, clear=True):
        # dict value takes precedence given a match
        assert config.get_config_val("var_one", config_dict=config_dict) == "a val"
        # but we fall back on the environment variables
        # if no match
        assert config.get_config_val("var_two", config_dict=config_dict) == "val2"
        # can use different keys for dict versus env
        assert (
            config.get_config_val(
                "var_2", config_dict=config_dict, env_variable_name="VAR_TWO"
            )
            == "val2"
        )
