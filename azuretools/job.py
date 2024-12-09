"""
Utilities for working with Azure Batch jobs.
"""

from azure.batch import BatchServiceClient, models


def create_job_if_not_exists(
    client: BatchServiceClient,
    job: models.JobAddParameter,
    verbose: bool = False,
    **kwargs,
) -> bool:
    """
    Create an Azure Batch job if it does
    not already exist, returning the job_id
    on success and ``None`` if the job already
    exists.

    Parameters
    ----------
    client
        :class:`BatchServiceClient` to use when
        creating the job.

    job
        :class:`JobAddParameter` instance defining
        the job to add.

    verbose
        Message to stdout if on success or failure
        due to job already existing? Default ``False``.

    **kwargs
        Additional keyword arguments passed to
        :meth:`BatchServiceClient.job.add`.

    Returns
    -------
    bool
        ``True`` if the job was created, ``False`` if
        it already existed.
    """
    try:
        client.job.add(job, **kwargs)
        if verbose:
            print(f"Created job {job.id}.")
        return True
    except models.BatchErrorException as e:
        if not e.error.code == "JobExists":
            raise e
        if verbose:
            print(f"Job {job.id} exists.")
        return False
