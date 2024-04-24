import numpy as np
from typing import List, Hashable
def sgs_algorithm(rcpsp_model: RCPSPModel, 
                  permutation_of_task: List[Hashable], predecessors=None):
    # Compute predecessors for each task. 
    if predecessors is None:
        predecessors = {k: set() for k in rcpsp_model.tasks_list}
        for k in rcpsp_model.successors:
            succ = rcpsp_model.successors[k]
            for s in succ:
                predecessors[s].add(k)
    # Store partial schedule
    schedule = {k: {"start_time": None,
                    "end_time": None}
                for k in rcpsp_model.tasks_list}
    # Duration of task
    duration_task = {k: rcpsp_model.mode_details[k][1]["duration"] for k in rcpsp_model.mode_details}
    # object to keep track of resource availability through time.
    resources_availability = {r: np.array(rcpsp_model.get_resource_availability_array(r))
                              for r in rcpsp_model.resources_list}
    # Store all the task that are added to the schedule.
    done = set()
    # Store the minimum starting time of a task.
    minimum_time = {t: 0 for t in rcpsp_model.tasks_list}
    while True:
        # Here, we select the next task in "permutation_of_task", whose all predecessors are done, and that is not done itself.
        next_task = next(x for x in permutation_of_task 
                         if all(p in done for p in predecessors[x]) 
                         and x not in done)
        # We distinguish task with 0 duration (for whcih we don't look at resource availability..)
        if duration_task[next_task] == 0:
            time_to_schedule_task = minimum_time[next_task]
        else:
            # Look for the smallest timestamp where the resource availability is >= than the resource demand of the task, 
            # and for the entire execution time of the task (hence the resources_availability[r][t:t+duration_task[next_task]])
            time_to_schedule_task = next(t for t in range(minimum_time[next_task], rcpsp_model.horizon)
                                         if 
                                         all(min(resources_availability[r][t:t+duration_task[next_task]])>=
                                             rcpsp_model.mode_details[next_task][1][r]
                                             for r in resources_availability))
        # We found the right time to schedule the task ! 
        schedule[next_task]["start_time"] = time_to_schedule_task
        schedule[next_task]["end_time"] = time_to_schedule_task+duration_task[next_task]
        # Update the resource availability with the task we just schedule.
        for r in resources_availability:
            need = rcpsp_model.mode_details[next_task][1][r]
            if r in rcpsp_model.non_renewable_resources:
                resources_availability[r][schedule[next_task]["start_time"]:]-=need
            else:
                resources_availability[r][schedule[next_task]["start_time"]:schedule[next_task]["end_time"]]-=need
        # Update the minimum time to start the successors of the task we just scheduled.
        for s in rcpsp_model.successors[next_task]:
            minimum_time[s] = max(minimum_time[s], schedule[next_task]["end_time"])
        # Adding current task to done, so we don't pick it later ! 
        done.add(next_task) 
        # If all tasks are done, we finish.
        if all(x in done for x in schedule):
            break
    return schedule  



