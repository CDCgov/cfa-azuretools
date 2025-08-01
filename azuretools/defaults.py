"""
Default configurations for Azure resources.
"""

from azure.mgmt.batch import models

from azuretools.autoscale import remaining_task_autoscale_formula

default_image_publisher = "microsoft-dsvm"
default_image_offer = "ubuntu-hpc"
default_image_sku = "2204"
default_node_agent_sku_id = "batch.node.ubuntu 22.04"


default_azure_batch_resource_url = "https://batch.core.windows.net/"
default_azure_batch_endpoint_subdomain = "batch.azure.com/"
default_azure_blob_storage_endpoint_subdomain = "blob.core.windows.net/"
default_azure_container_registry_domain = "azurecr.io"

default_image_reference = models.ImageReference(
    publisher=default_image_publisher,
    offer=default_image_offer,
    sku=default_image_sku,
    version="latest",
)

# this default sets up pools to use containers but does not
# pre-fetch any
default_container_configuration = models.ContainerConfiguration(
    type="dockerCompatible",
)

default_vm_configuration = models.VirtualMachineConfiguration(
    image_reference=default_image_reference,
    container_configuration=default_container_configuration,
    node_agent_sku_id=default_node_agent_sku_id,
)


default_vm_size = "standard_d4s_v3"  # 4 core D-series VM

default_autoscale_evaluation_interval = "PT5M"  # every 5 minutes

default_autoscale_formula = remaining_task_autoscale_formula()

default_network_config_dict = dict(
    public_ip_address_configuration=models.PublicIPAddressConfiguration(
        provision="NoPublicIPAddresses"
    )
)


default_pool_config_dict = dict(
    deployment_configuration=models.DeploymentConfiguration(
        virtual_machine_configuration=default_vm_configuration
    ),
    vm_size=default_vm_size,
    target_node_communication_mode="Simplified",
    scale_settings=models.ScaleSettings(
        auto_scale=models.AutoScaleSettings(
            formula=default_autoscale_formula,
            evaluation_interval=default_autoscale_evaluation_interval,
        )
    ),
)


def get_default_pool_identity(
    user_assigned_identity: str,
) -> models.BatchPoolIdentity:
    """
    Get the default :class:`models.BatchPoolIdentity`
    instance for azuretools (which associates a blank
    `class:`models.UserAssignedIdentities` instance
    to the provided ``user_assigned_identity``
    string.

    Parameters
    ----------
    user_assigned_identity
        User-assigned identity, as a string.

    Returns
    -------
    models.BatchPoolIdentity
        Instantiated :class:`BatchPoolIdentity`` instance
        using the provided user-assigned identity.
    """
    return models.BatchPoolIdentity(
        type=models.PoolIdentityType.user_assigned,
        user_assigned_identities={
            user_assigned_identity: models.UserAssignedIdentities()
        },
    )


def get_default_pool_config(
    pool_name: str, subnet_id: str, user_assigned_identity: str, **kwargs
) -> models.Pool:
    """
    Instantiate a :class:`azure.mgmt.batch.models.Pool`
    instance with the given pool name and subnet id,
    the default pool identity given by
    :func:`get_default_pool_identity`, and other defaults
    specified in :obj:`default_pool_config_dict` and
    :obj:`default_network_config_dict`.

    Parameters
    ----------
    pool_name
        Name for the pool. Passed as the ``display_name``
        argument to the :class:`models.Pool` constructor.

    subnet_id
        Subnet id for the pool, as a string. Should typically
        be obtained from a configuration file or an environment
        variable, often via a :class:`CredentialHandler` instance.

    user_assigned_identity
        User-assigned identity for the pool, as a string.
        Passed to :func:`get_default_pool_identity`.

    **kwargs
        Additional keyword arguments passed to the
        :class:`models.Pool` constructor, potentially
        overriding settings from :obj:`default_pool_config_dict`.

    Returns
    -------
    models.Pool
       The instantiated :class:`models.Pool` object.
    """
    return models.Pool(
        identity=get_default_pool_identity(user_assigned_identity),
        display_name=pool_name,
        network_configuration=models.NetworkConfiguration(
            subnet_id=subnet_id, **default_network_config_dict
        ),
        **{**default_pool_config_dict, **kwargs},
    )


def assign_container_config(
    pool_config: models.Pool, container_config: models.ContainerConfiguration
) -> models.Pool:
    """
    Assign a container configuration to a models.Pool object
    (in place).

    Parameters
    ----------
    pool_config
        :class:`models.Pool` configuration object to modify.

    container_config
        :class:`models.ContainerConfiguration` object to
        add to the :class:`models.Pool` configuration object.

    Returns
    -------
    models.Pool
        The modified :class:`models.Pool` object.
    """
    (
        pool_config.deployment_configuration.virtual_machine_configuration.container_configuration
    ) = container_config
    return pool_config
