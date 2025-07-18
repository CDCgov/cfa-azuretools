"""
Functions to assist in configuring Azure
Batch autoscaling.
"""


def remaining_task_autoscale_formula(
    max_number_vms: int = 10, task_type_to_count: str = "PendingTasks"
):
    """
    Get an autoscaling formula that rescales pools based on the remaining task count.
    and scales down to zero when no tasks remain.

    Parameters
    ----------
    max_number_vms
        Maximum number of virtual machines to spin
        up, regardless of the number of remaining
        tasks. Default 10.

    task_type_to_count
        Name in batch of the task type to count.
        See `Read-only service-defined variables
        <https://learn.microsoft.com/en-us/azure/batch/batch-automatic-scaling#read-only-service-defined-variables>`_
        in the Batch docs. Default `PendingTasks`: the number of tasks that are either already
        running on a node or are ready to be picked up by an available node.

    Returns
    -------
    str
        The autoscale formula, as a string.
    """
    autoscale_formula_template = """
$tasks = max(0, ${task_type_to_count}.GetSample(1));
// If number of tasks is not 0, set targetVM to pending tasks, otherwise 0.
$targetVMs = $tasks > 0 ? $tasks : 0;
// The pool size is capped at {max_number_vms}, if target VM value is more than that, set it to {max_number_vms}.
cappedPoolSize = {max_number_vms};
$TargetDedicatedNodes = max(0, min($targetVMs, cappedPoolSize));
// Set node deallocation mode - keep nodes active only until tasks finish
$NodeDeallocationOption = taskcompletion;
    """
    autoscale_formula = autoscale_formula_template.format(
        max_number_vms=max_number_vms,
        task_type_to_count=task_type_to_count,
    )

    return autoscale_formula
