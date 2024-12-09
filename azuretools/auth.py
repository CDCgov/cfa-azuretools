"""
Helper functions for Azure authentication.
"""

from dataclasses import dataclass
from functools import cached_property, partial

from azure.batch import models
from azure.common.credentials import ServicePrincipalCredentials
from azure.identity import (
    AzureCliCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
)
from azure.keyvault.secrets import SecretClient

from azuretools.config import get_config_val
from azuretools.util import ensure_listlike
from azuretools.validate import is_valid_acr_endpoint


@dataclass
class CredentialHandler:
    """
    Data structure for Azure credentials.
    Lazy and cached: credentials are retrieved
    from a keyvault only when needed
    and are cached thereafter.
    """

    azure_subscription_id: str = None
    azure_resource_group_name: str = None
    azure_user_assigned_identity: str = None
    azure_subnet_id: str = None

    azure_keyvault_endpoint: str = None
    azure_keyvault_sp_secret_id: str = None
    azure_tenant_id: str = None
    azure_sp_client_id: str = None
    azure_batch_endpoint_subdomain: str = "batch.azure.com/"
    azure_batch_account: str = None
    azure_batch_location: str = None
    azure_batch_resource_url: str = "https://batch.core.windows.net/"
    azure_blob_storage_endpoint_subdomain: str = "blob.core.windows.net/"
    azure_blob_storage_account: str = None

    azure_container_registry_account: str = None
    azure_container_registry_domain: str = "azurecr.io"

    def require_attr(self, attributes: str | list[str], goal: str = None):
        """
        Check that attributes required for a given operation are defined.
        Raises an informative error message if the required attribute is not defined.

        Parameters
        ----------
        attributes
            String of list of strings naming the required
            attribute(s).

        goal
            String naming the value that the attributes
            are required for obtaining, to make error
            messages more informative. If ``None``,
            use a more generic message. Default ``None``.

        Returns
        -------
        None
            ``None`` on success.

        Raises
        ------
        AttributeError
            If any required ``attributes`` are ``None``.
        """
        attributes = ensure_listlike(attributes)
        for attr in attributes:
            attr_val = getattr(self, attr)
            if attr_val is None:
                err_msg = (
                    f"A non-None value for attribute {attr} " "is required "
                ) + (
                    f"to obtain a value for {goal}."
                    if goal is not None
                    else "for this operation."
                )
                raise AttributeError(err_msg)

    @property
    def azure_batch_endpoint(self) -> str:
        """
        Azure batch endpoint URL.
        Constructed programmatically from account
        name, location, and subdomain.

        Returns
        -------
        str
           The endpoint URL.
        """
        self.require_attr(
            [
                "azure_batch_account",
                "azure_batch_location",
                "azure_batch_endpoint_subdomain",
            ],
            goal="Azure batch endpoint URL",
        )
        return (
            f"https://{self.azure_batch_account}."
            f"{self.azure_batch_location}."
            f"{self.azure_batch_endpoint_subdomain}"
        )

    @property
    def azure_blob_storage_endpoint(self) -> str:
        """
        Azure blob storage endpoint URL.
        Constructed programmatically from the
        account name and endpoint subdomain.

        Returns
        -------
        str
           The endpoint URL.
        """
        self.require_attr(
            [
                "azure_blob_storage_account",
                "azure_blob_storage_endpoint_subdomain",
            ],
            goal="Azure blob storage endpoint URL",
        )
        return (
            f"https://{self.azure_blob_storage_account}."
            f"{self.azure_blob_storage_endpoint_subdomain}"
        )

    @property
    def azure_container_registry_endpoint(self) -> str:
        """
        Azure container registry endpoint URL.
        Constructed programmatically from the account name
        and endpoint subdomain.

        Returns
        -------
        str
           The endpoint URL.
        """
        self.require_attr(
            [
                "azure_container_registry_account",
                "azure_container_registry_domain",
            ],
            goal="Azure container registry endpoint URL",
        )
        return (
            f"{self.azure_container_registry_account}."
            f"{self.azure_container_registry_domain}"
        )

    @cached_property
    def user_credential(self) -> ChainedTokenCredential:
        """
        Azure user credential.

        Returns
        -------
        ChainedTokenCredential
            The Azure user credential.
        """
        credential_order = (AzureCliCredential(),)
        return ChainedTokenCredential(*credential_order)

    @cached_property
    def service_principal_secret(self):
        """
        A service principal secret.

        Returns
        -------
        str
            The secret.
        """
        self.require_attr(
            ["azure_keyvault_endpoint", "azure_keyvault_sp_secret_id"],
            goal="service_principal_secret",
        )

        return get_sp_secret(
            self.azure_keyvault_endpoint,
            self.azure_keyvault_sp_secret_id,
            self.user_credential,
        )

    @cached_property
    def batch_service_principal_credentials(self):
        """
        Service Principal credentials for authenticating to Azure Batch.

        Returns
        -------
        ServicePrincipalCredentials
            The credentials.
        """
        self.require_attr(
            [
                "azure_tenant_id",
                "azure_sp_client_id",
                "azure_batch_resource_url",
            ],
            goal="batch_service_principal_credentials",
        )
        return ServicePrincipalCredentials(
            client_id=self.azure_sp_client_id,
            tenant=self.azure_tenant_id,
            secret=self.service_principal_secret,
            resource=self.azure_batch_resource_url,
        )

    @cached_property
    def client_secret_sp_credential(self):
        """
        A client secret credential created using ``self.service_principal_secret``.

        Returns
        -------
        ClientSecretCredential
            The credential.
        """
        self.require_attr(["azure_tenant_id", "azure_sp_client_id"])
        return ClientSecretCredential(
            tenant_id=self.azure_tenant_id,
            client_secret=self.service_principal_secret,
            client_id=self.azure_sp_client_id,
        )

    @cached_property
    def compute_node_identity_reference(self):
        """
        An object defining a compute node identity reference.

        Specifically, a :class:`models.ComputeNodeIdentityReference`
        object associated to the :class:`CredentialHandler`'s
        user-assigned identity.

        Returns
        -------
        models.ComputeNodeIdentityReference
            The identity reference.
        """
        self.require_attr(
            ["azure_user_assigned_identity"],
            goal="Compute node identity reference",
        )
        return models.ComputeNodeIdentityReference(
            resource_id=self.azure_user_assigned_identity
        )

    @cached_property
    def azure_container_registry(self):
        """
        An object pointing to an Azure Container Registry.

        Specifically, a :class:`models.ContainerRegistry` instance
        corresponding to the particular Azure Container
        Registry account specified in the
        :class:`CredentialHandler`, if any, with authentication
        via the ``compute_node_identity_reference`` defined by
        :class:`CredentialHandler`, if any.

        Returns
        -------
        models.ContainerRegistry
            A properly instantiated :class:`models.ContainerRegistry`
            object.
        """
        self.require_attr(
            [
                "azure_container_registry_account",
                "azure_container_registry_domain",
                "azure_user_assigned_identity",
            ],
            goal=("Azure Container Registry " "`ContainerRegistry` instance"),
        )

        server = f"https://{self.azure_container_registry_endpoint}"

        valid, msg = is_valid_acr_endpoint(server)
        if not valid:
            raise ValueError(msg)

        return models.ContainerRegistry(
            user_name=self.azure_container_registry_account,
            registry_server=server,
            identity_reference=self.compute_node_identity_reference,
        )


class EnvCredentialHandler(CredentialHandler):
    """
    Azure Credentials populated from available environment variables.

    Subclass of :class:`CredentialHandler` that populates attributes
    from environment variables at instantiation, with the opportunity
    to override those values via keyword arguments passed to the
    constructor.

    Parameters
    ----------
    **kwargs
        Keyword arguments defining additional attributes
        or overriding those set in the environment variables.
        Passed as the ``config_dict`` argument to
        :func:`get_config_val`.
    """

    def __init__(self, **kwargs) -> None:
        # numpydoc ignore=PR01
        """
        Default constructor.
        """
        get_conf = partial(get_config_val, config_dict=kwargs, try_env=True)

        for key in self.__dataclass_fields__.keys():
            self.__setattr__(key, get_conf(key))


def get_sp_secret(
    vault_url: str,
    vault_sp_secret_id: str,
    user_credential: ChainedTokenCredential = None,
) -> str:
    """
    Get a service principal secret from an Azure keyvault.

    Parameters
    ----------
    vault_url
       URL for the Azure keyvault to access.
    vault_sp_secret_id
       Service principal secret ID within the keyvault.
    user_credential
       User credential for the Azure user, as an
       azure-identity :class:`UserCredential` class instance.
       If `None`, attempt to use a :class:`ChainedTokenCredential`
       instantiated at runtime that prefers, in order,
       a newly instantiated :class:`AzureCliCredential` (get
       credentials associated to the user logged in via
       the Azure CLI (i.e. ``az login`` at the command line).
       Default ``None``.

    Returns
    -------
    str
        The retrieved value of the service principal secret.
    """
    if user_credential is None:
        credential_order = (AzureCliCredential(),)
        user_credential = ChainedTokenCredential(*credential_order)

    secret_client = SecretClient(
        vault_url=vault_url, credential=user_credential
    )
    sp_secret = secret_client.get_secret(vault_sp_secret_id).value

    return sp_secret


def get_client_secret_sp_credential(
    vault_url: str,
    vault_sp_secret_id: str,
    tenant_id: str,
    application_id: str,
    user_credential: ChainedTokenCredential = None,
) -> ClientSecretCredential:
    """
    Get a ClientSecretCredential for a given Azure service principal.

    Parameters
    ----------
    vault_url
       URL for the Azure keyvault to access.
    vault_sp_secret_id
       Service principal secret ID within the keyvault.
    tenant_id
       Tenant ID for the service principal credential.
    application_id
       Application ID for the service principal credential.
    user_credential
       User credential for the Azure user, as an
       azure-identity UserCredential class instance.
       Passed to :func:`get_sp_secret`.
       If None, get_sp_secret() will attempt to use a
       :class:`ChainedTokenCredential` instantiated at runtime.
       See its documentation for more.
       Default ``None``.

    Returns
    -------
    ClientSecretCredential
        A :class:`ClientSecretCredential`
        for the given service principal.
    """
    sp_secret = get_sp_secret(
        vault_url, vault_sp_secret_id, user_credential=user_credential
    )
    sp_credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=application_id,
        client_secret=sp_secret,
    )

    return sp_credential


def get_service_principal_credentials(
    vault_url: str,
    vault_sp_secret_id: str,
    tenant_id: str,
    application_id: str,
    resource_url: str = "https://batch.core.windows.net/",
    user_credential: ChainedTokenCredential = None,
) -> ServicePrincipalCredentials:
    """
    Get a :class:`ServicePrincipalCredentials` object for a given Azure service principal.

    Parameters
    ----------
    vault_url
       URL for the Azure keyvault to access.
    vault_sp_secret_id : str
       Service principal secret ID within the keyvault.
    tenant_id
       Tenant ID for the service principal credential.
    application_id
       Application ID for the service principal credential.
    resource_url
       URL of the Azure resource. Default
       ``https://batch.core.windows.net/``.
    user_credential
       User credential for the Azure user, as an
       azure-identity UserCredential class instance.
       Passed to :func:`get_sp_secret`.
       If ``None``, :func:`get_sp_secret` will attempt to use a
       :class:`ChainedTokenCredential` instantiated at runtime.
       See the :func:`get_sp_secret` documentation for details.
       Default ``None``.

    Returns
    -------
    ServicePrincipalCredentials
        A :class:`ServicePrincipalCredentials`
        object for the service principal.
    """
    sp_secret = get_sp_secret(
        vault_url, vault_sp_secret_id, user_credential=user_credential
    )
    sp_credential = ServicePrincipalCredentials(
        tenant=tenant_id,
        client_id=application_id,
        secret=sp_secret,
        resource=resource_url,
    )

    return sp_credential


def get_compute_node_id_reference(
    config_dict: dict = None,
    try_env: bool = True,
) -> models.ComputeNodeIdentityReference:
    """
    Get a valid :class:`models.ComputeNodeIdentityReference` value
    by querying the provided configuration dictionary or the
    available environment variables.

    Parameters
    ----------
    config_dict
       Configuration dictionary in which to look
       for relevant keys. Passed to
       :func:`get_config_val`. Default ``None``.

    try_env
       Look for configuration keys in the
       environment variables if they are not
       available in the config_dict? Passed
       to :func:`get_config_val`. Default ``True``.

    Returns
    -------
    models.ComputeNodeIdentityReference
        A :class:`models.ComputeNodeIdentityReference`
        created according to the specified configuration.
    """
    return models.ComputeNodeIdentityReference(
        resource_id=get_config_val(
            "azure_user_assigned_identity", config_dict=config_dict
        )
    )
