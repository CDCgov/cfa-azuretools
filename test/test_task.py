from azure.batch.models import (
    AutoUserScope,
    AutoUserSpecification,
    ComputeNodeIdentityReference,
    ElevationLevel,
    OutputFile,
    OutputFileBlobContainerDestination,
    OutputFileDestination,
    OutputFileUploadOptions,
    TaskAddParameter,
    TaskContainerSettings,
    UserIdentity,
)

from azuretools.task import get_task_config


def test_get_task_config_no_custom_arguments():
    task_id = "test-task"
    base_call = "echo Hello, World!"

    task_config = get_task_config(task_id, base_call)

    assert isinstance(task_config, TaskAddParameter)
    assert task_config.id == task_id
    assert task_config.command_line == base_call
    assert task_config.container_settings is None
    assert task_config.user_identity is not None
    assert isinstance(task_config.user_identity, UserIdentity)
    assert task_config.user_identity.auto_user.scope == AutoUserScope.pool
    assert task_config.user_identity.auto_user.elevation_level == ElevationLevel.admin


def test_get_task_config_with_custom_container_settings():
    task_id = "test-task"
    base_call = "echo Hello, World!"
    container_settings = TaskContainerSettings(image_name="test-image")

    task_config = get_task_config(
        task_id, base_call, container_settings=container_settings
    )
    assert isinstance(task_config, TaskAddParameter)
    assert task_config.id == task_id
    assert task_config.command_line == base_call
    assert task_config.container_settings == container_settings


def test_get_task_config_with_custom_user_identity():
    task_id = "test-task"
    base_call = "echo Hello, World!"
    user_identity = UserIdentity(
        auto_user=AutoUserSpecification(
            scope=AutoUserScope.task, elevation_level=ElevationLevel.non_admin
        )
    )

    task_config = get_task_config(task_id, base_call, user_identity=user_identity)

    assert isinstance(task_config, TaskAddParameter)
    assert task_config.id == task_id
    assert task_config.command_line == base_call
    assert task_config.user_identity == user_identity


def test_get_task_config_with_additional_kwargs():
    task_id = "test-task"
    base_call = "echo Hello, World!"
    custom_env_settings = [{"name": "ENV_VAR", "value": "value"}]

    task_config = get_task_config(
        task_id, base_call, environment_settings=custom_env_settings
    )

    assert task_config.id == task_id
    assert task_config.command_line == base_call
    assert task_config.environment_settings == custom_env_settings


def test_get_task_config_auto_log():
    task_id = "test_task_2"
    base_call = "echo 'this is a test'"
    blob_container = "my_log_container"
    blob_account = "my_blob_account"
    log_subdir = "my_log_subdir"
    node_id_ref = ComputeNodeIdentityReference()
    upload_condition = "taskCompletion"
    task_config = get_task_config(
        task_id,
        base_call,
        log_blob_container=blob_container,
        log_blob_account=blob_account,
        log_subdir=log_subdir,
        log_compute_node_identity_reference=node_id_ref,
    )

    assert isinstance(task_config, TaskAddParameter)
    assert task_config.id == task_id
    assert task_config.command_line == base_call
    assert len(task_config.output_files) == 1
    outfile = task_config.output_files[0]
    assert isinstance(outfile, OutputFile)
    assert outfile.file_pattern == "../std*.txt"
    destination = outfile.destination
    assert isinstance(destination, OutputFileDestination)
    assert isinstance(destination.container, OutputFileBlobContainerDestination)
    assert (
        destination.container.container_url
        == f"https://{blob_account}.blob.core.windows.net/{blob_container}"
    )
    assert destination.container.path == f"{log_subdir}/{task_id}"
    assert destination.container.identity_reference == node_id_ref
    assert isinstance(outfile.upload_options, OutputFileUploadOptions)
    assert outfile.upload_options.upload_condition == upload_condition
