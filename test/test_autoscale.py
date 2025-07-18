import pytest

from azuretools.autoscale import remaining_task_autoscale_formula

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


@pytest.mark.parametrize(
    ["task_type_to_count", "max_number_vms"],
    [
        ["ActiveTasks", 5],
        ["ActiveTasks", 15],
        ["PendingTasks", 102],
        ["RunningTasks", 5],
    ],
)
def test_remaining_task_formula(task_type_to_count, max_number_vms):
    assert remaining_task_autoscale_formula(
        max_number_vms, task_type_to_count
    ) == autoscale_formula_template.format(
        task_type_to_count=task_type_to_count, max_number_vms=max_number_vms
    )


def test_remaining_task_formula_default():
    assert (
        remaining_task_autoscale_formula()
        == autoscale_formula_template.format(
            task_type_to_count="PendingTasks", max_number_vms=10
        )
    )
