def sgs_algorithm(rcpsp_problem: RcpspProblem,
                  permutation_of_task: List[Hashable],
                  predecessors: dict[Hashable, set[Hashable]]=None):
    # Compute a predecessors mapping for each task. 
    if predecessors is None:
        predecessors = {k: set() for k in rcpsp_problem.tasks_list}
        for k in rcpsp_problem.successors:
            succ = rcpsp_problem.successors[k]
            for s in succ:
                predecessors[s].add(k)

    # Pre-compute durations for each task (assuming mode 1)
    duration_task = {k: rcpsp_problem.mode_details[k][1]["duration"] for k in rcpsp_problem.tasks_list}
    # Pre-compute resource needs for each task
    resource_consumptions = {k: {r: rcpsp_problem.mode_details[k][1].get(r, 0) for r in rcpsp_problem.resources_list}
                             for k in rcpsp_problem.tasks_list}
    # Initialize the schedule dictionary to store start and end times
    schedule = {t: {"start_time": None, "end_time": None} for t in rcpsp_problem.tasks_list}
    # Resource availability is tracked over the project horizon.
    # It's a dictionary of arrays, one for each resource.
    resources_availability = {r: np.array(rcpsp_problem.get_resource_availability_array(r))
                              for r in rcpsp_problem.resources_list}
    
    # Set of tasks that are already scheduled and finished.
    completed_tasks = set()

    # The source task is the first to be scheduled, at time 0.
    source_task = rcpsp_problem.source_task
    schedule[source_task]["start_time"] = 0
    schedule[source_task]["end_time"] = 0
    completed_tasks.add(source_task)

    # Main loop: continue until all tasks are scheduled
    while len(completed_tasks) < rcpsp_problem.n_jobs:
        # 1. Find the next eligible task from the permutation
        next_task = next(p for p in permutation_of_task 
                         if p not in completed_tasks and all(pred in completed_tasks for pred in predecessors.get(p, set())))        
        # 2. Determine the earliest start time based on PRECEDENCE constraints
        # This is the maximum of the end times of all its predecessors.
        earliest_start_by_pred = 0
        if len(predecessors.get(next_task, set())) > 0:
            earliest_start_by_pred = max([schedule[pred]["end_time"] for pred in predecessors[next_task]])

        # 3. Find the final start time by also considering RESOURCE constraints
        # Starting from earliest_start_by_pred, find the first time slot 't'
        # where all required resources are available for the task's full duration.
        if duration_task[next_task] == 0:
            start_of_task = earliest_start_by_pred
        else:
            start_of_task = next(i for i in range(earliest_start_by_pred, 2*rcpsp_problem.horizon)
                                 if all(np.min(resources_availability[r][i:i+duration_task[next_task]])>=resource_consumptions[next_task][r]
                                        for r in rcpsp_problem.resources_list))
        # ... Your implementation here ...
        # 4. Schedule the task and update resource availability
        schedule[next_task] = {"start_time": start_of_task, "end_time": start_of_task + duration_task[next_task]}
        if duration_task[next_task] > 0:
            for r in rcpsp_problem.resources_list:
                resources_availability[r][start_of_task:start_of_task + duration_task[next_task]] -= resource_consumptions[next_task][r]
        # 5. Add the task to the set of completed tasks
        completed_tasks.add(next_task)

    return schedule