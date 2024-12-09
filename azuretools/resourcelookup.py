"""
Tools for looking up available Azure resources.
"""

from azure.mgmt.batch import BatchManagementClient
from azure.mgmt.batch.models import SupportedSku

from azuretools.client import get_batch_management_client
from azuretools.config import get_config_val


def sku_to_dict(sku: SupportedSku):
    """
    Convert a :class:`SupportedSku` object to
    a flat dictionary or property names
    and values.

    Parameters
    ----------
    sku
        The :class:`SupportedSku` object to convert.

    Returns
    -------
    dict
       A flat dictionary with keys ``'name'``,
       ``'family_name'``, ``'batch_support_end_of_life'``,
       ``'additional_properties'``, as well as keys
       and values corresponding to any
       :class:`~azure.mgmt.batch.models.SkuCapability`
       objects associated to the :class:`SupportedSku`.
    """
    return dict(
        name=sku.name,
        family_name=sku.family_name,
        batch_support_end_of_life=sku.batch_support_end_of_life,
        additional_properties=sku.additional_properties,
        **{c.name: c.value for c in sku.capabilities},
    )


def lookup_available_vm_skus_for_batch(
    client: BatchManagementClient = None,
    config_dict: dict = None,
    try_env: bool = True,
    to_dict: bool = True,
    **kwargs,
):
    """
    Look up available VM image
    SKUs for the given batch service.

    Parameters
    ----------
    client
        :class:`BatchManagementClient` to use
        when looking up the available images.
        If ``None``, use the output of
        :func:`get_batch_management_client()`.
        Default ``None``.

    config_dict
        Configuration dictionary. Passed as the
        ``config_dict`` argument to any internal
        :func:`config.get_config_val` calls.
        See that function's documentation
        for additional details.

    try_env
        Whether to look for configuration values
        in the available environment variables.
        Passed as the ``try_env`` argument to
        to any internal :func:`config.get_config_val`
        calls. See that function's documentation
        for additional details.

    to_dict
        Apply :func:`sku_to_dict` to the list of results?
        Default ``True``. If ``False``, the result will be
        a list of :class:`SupportedSku` objects.

    **kwargs
        Additional keyword arguments passed to
        :meth:`BatchManagementClient.location.list_supported_virtual_machine_skus`.

    Returns
    -------
    list
       Of supported SKUs, either as dictionaries of property
       names and values (default) or as raw :class:`SupportedSku`
       objects (if ``to_dict`` is ``False``).
    """
    if client is None:
        client = get_batch_management_client(
            config_dict=config_dict, try_env=try_env
        )
    result = [
        item
        for item in client.location.list_supported_virtual_machine_skus(
            location_name=get_config_val(
                "azure_batch_location",
                config_dict=config_dict,
                try_env=try_env,
            ),
            **kwargs,
        )
    ]

    if to_dict:
        result = [sku_to_dict(x) for x in result]

    return result
