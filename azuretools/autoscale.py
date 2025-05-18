"""
Functions to assist in configuring Azure
batch autoscaling.
"""


def remaining_task_autoscale_formula(
    evaluation_interval: str = "PT5M",
    task_sample_interval_minutes: int = 15,
    max_number_vms: int = 10,
):
    """
    Get an autoscaling formula that rescales pools based on the remaining task count.

    Parameters
    ----------
    evaluation_interval
        How often to evaluate the formula, as a
        `Java-style duration string
        <https://docs.oracle.com/javase/8/docs/api/java/time/Duration.html#parse-java.lang.CharSequence->`_.
        Default ``"PT5M"``: every 5 minutes.

    task_sample_interval_minutes
        Task sampling interval, in minutes, as an integer.
        Default 15.

    max_number_vms
        Maximum number of virtual machines to spin
        up, regardless of the number of remaining
        tasks. Default 10.

    Returns
    -------
    str
        The autoscale formula, as a string.
    """
    autoscale_formula_template = """// In this example, the pool size
// is adjusted based on the number of tasks in the queue.
// Note that both comments and line breaks are acceptable in formula strings.

// Get pending tasks for the past 15 minutes.
$samples = $ActiveTasks.GetSamplePercent(TimeInterval_Minute * {task_sample_interval_minutes});
// If we have fewer than 70 percent data points, we use the last sample point, otherwise we use the maximum of last sample point and the history average.
$tasks = $samples < 70 ? max(0, $ActiveTasks.GetSample(1)) :
max( $ActiveTasks.GetSample(1), avg($ActiveTasks.GetSample(TimeInterval_Minute * {task_sample_interval_minutes})));
// If number of pending tasks is not 0, set targetVM to pending tasks, otherwise half of current dedicated.
$targetVMs = $tasks > 0 ? $tasks : max(0, $TargetDedicatedNodes / 2);
// The pool size is capped at {max_number_vms}, if target VM value is more than that, set it to {max_number_vms}.
cappedPoolSize = {max_number_vms};
$TargetDedicatedNodes = max(0, min($targetVMs, cappedPoolSize));
// Set node deallocation mode - keep nodes active only until tasks finish
$NodeDeallocationOption = taskcompletion;"""

    autoscale_formula = autoscale_formula_template.format(
        task_sample_interval_minutes=task_sample_interval_minutes,
        max_number_vms=max_number_vms,
    )

    return autoscale_formula
