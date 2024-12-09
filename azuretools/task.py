"""
Functions for manipulating tasks within an
Azure batch job.
"""

import azure.batch.models as batchmodels
from azure.batch.models import (
    ContainerRegistry,
    ContainerWorkingDirectory,
    TaskContainerSettings,
    UserIdentity,
)


def create_bind_mount_string(
    az_mount_dir: str, source_path: str, target_path: str
) -> str:
    """
    Create a valid OCI bind mount string for
    an OCI container running in Azure batch and
    mounting things from Azure blob storage.

    Parameters
    ----------
    az_mount_dir
        Directory in which to look for directories
        or volumes to mount.

    source_path
        Path relative to az_mount_dir to use as the source.

    target_path
        Absolute path within the container to bind to
        the source path.

    Returns
    -------
    str
        A properly formatted OCI --mount type=bind command,
        as a string.
    """
    mount_template = "--mount type=bind,source={}/{},target={}"
    return mount_template.format(az_mount_dir, source_path, target_path)


def get_container_settings(
    container_image_name: str,
    az_mount_dir: str = "$AZ_BATCH_NODE_MOUNTS_DIR",
    working_directory: str | ContainerWorkingDirectory = None,
    mount_pairs: list[dict] = None,
    additional_options: str = "",
    registry: ContainerRegistry = None,
    **kwargs,
):
    """
    Create a valid set of container settings with
    bind mounts specified in mount_pairs, for an
    OCI container run in an Azure batch task.

    Parameters
    ----------
    container_image_name
        Name of the OCI container image to use.

    az_mount_dir
        Directory in which to look for directories
        or volumes to mount.

    working_directory
        Working directory for the task within the
        container, passed as the working_directory parameter
        to the TaskContainerSettings constructor.
        If None (the default), then defer
        to the Azure batch default (note that this will
        _not_ typically be the same as the container
        image's own WORKDIR). Otherwise specify it with
        a TaskWorkingDirectory instance or use the string
        "containerImageDefault" to use the container's own
        WORKDIR. See the documentation for
        class::`TaskContainerSettings` for more details.

    mount_pairs
        Pairs of 'source' and 'target' directories to mount
        when the container is run, as a list of dictionaries
        with 'source' and 'target' keys.

    additional_options
        Additional flags and options to pass to the container
        run command, as a string. Default "".

    registry
        :class:`ContainerRegistry` instance specifying
        a private container registry from which to fetch
        task containers. Default ``None``.

    **kwargs
        Additional keyword arguments passed to the
        :class:`TaskContainerSettings` constructor.

    Returns
    -------
    TaskContainerSettings
        A :class:`TaskContainerSettings` object
        instantiated according to the specified input.
    """

    ctr_r_opts = additional_options

    for pair in mount_pairs:
        ctr_r_opts += " " + create_bind_mount_string(
            az_mount_dir, pair["source"], pair["target"]
        )

    return TaskContainerSettings(
        image_name=container_image_name,
        working_directory=working_directory,
        container_run_options=ctr_r_opts,
        registry=registry,
        **kwargs,
    )


def get_task_config(
    task_id: str,
    base_call: str,
    container_settings: TaskContainerSettings = None,
    user_identity: UserIdentity = None,
) -> None:
    """
    Create a batch task with a given base call
    and set of container settings.

    If the ``user_identity`` is not set, set it up
    automatically with sufficient permissions to
    read and write from mounted volumes.

    Parameters
    ----------
    task_id
        Alphanmueric identifier for the task.

    base_call
        The base command line call for the task, as a string.

    container_settings
        Container settings for the task. You can use
        the create_container_settings helper function
        to create a valid entry. Default ``None``.

    user_identity : UserIdentity
        User identity under which to run the task.
        If ``None``, create one automatically with admin
        privileges, if permitted. Default ``None``.

    Returns
    -------
    TaskAddParameter
       The task configuration object.
    """
    if user_identity is None:
        user_identity = UserIdentity(
            auto_user=batchmodels.AutoUserSpecification(
                scope=batchmodels.AutoUserScope.pool,
                elevation_level=batchmodels.ElevationLevel.admin,
            )
        )
    task_config = batchmodels.TaskAddParameter(
        id=task_id,
        command_line=base_call,
        container_settings=container_settings,
        user_identity=user_identity,
    )

    return task_config
