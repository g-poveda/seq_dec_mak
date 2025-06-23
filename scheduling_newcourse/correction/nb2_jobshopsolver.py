from typing import List
from ortools.sat.python import cp_model
from typing import Tuple


class SolutionJobshop:
    def __init__(self, schedule: List[List[Tuple[int, int]]]):
        # For each job and subjob, start and end time given as tuple of int.
        self.schedule = schedule


class Subjob:
    machine_id: int
    processing_time: int

    def __init__(self, machine_id, processing_time):
        self.machine_id = machine_id
        self.processing_time = processing_time


class JobShopProblem:
    n_jobs: int
    n_machines: int
    list_jobs: List[List[Subjob]]

    def __init__(self, list_jobs: List[List[Subjob]], n_jobs: int = None, n_machines: int = None):
        self.n_jobs = n_jobs
        self.n_machines = n_machines
        self.list_jobs = list_jobs
        if self.n_jobs is None:
            self.n_jobs = len(list_jobs)
        if self.n_machines is None:
            self.n_machines = len(set([y.machine_id for x in self.list_jobs
                                       for y in x]))
        # Store for each machine the list of subjob given as (index_job, index_subjob)
        self.job_per_machines = {i: [] for i in range(self.n_machines)}
        for k in range(self.n_jobs):
            for sub_k in range(len(list_jobs[k])):
                self.job_per_machines[list_jobs[k][sub_k].machine_id] += [(k, sub_k)]


class SolverJobShop:
    def __init__(self, jobshop_problem: JobShopProblem):
        self.jobshop_problem = jobshop_problem
        self.model = cp_model.CpModel()
        self.variables = {}
    
    def init_model(self, **kwargs):
        # 1. Define the Horizon (a safe upper bound for the makespan)
        # A simple heuristic is to sum all processing times.
        horizon = sum(sub.processing_time 
                      for job in self.jobshop_problem.list_jobs 
                      for sub in job)

        # 2. Create Decision Variables
        # --- YOUR CODE HERE ---
        # TO DO: Loop through each job and each subjob in self.jobshop_problem.
        # For each, create a start, end, and interval variable using the model.
        # Use the 'horizon' as the upper bound for start/end variables.
        # Store these new variables in the corresponding dictionaries in self.variables.
        # Example key: (job_id, subjob_id)
        starts = [[self.model.NewIntVar(0, horizon, f"starts_{j,k}")
                   for k in range(len(self.jobshop_problem.list_jobs[j]))]
                   for j in range(self.jobshop_problem.n_jobs)]
        ends = [[self.model.NewIntVar(0, horizon, f"starts_{j,k}")
                 for k in range(len(self.jobshop_problem.list_jobs[j]))]
                 for j in range(self.jobshop_problem.n_jobs)]
        intervals = [[self.model.NewIntervalVar(start=starts[j][k],
                                                size=self.jobshop_problem.list_jobs[j][k].processing_time,
                                                end=ends[j][k],
                                                name=f"task_{j, k}")
                     for k in range(len(self.jobshop_problem.list_jobs[j]))]
                     for j in range(self.jobshop_problem.n_jobs)]
        self.variables["starts"] = starts
        self.variables["ends"] = ends
        
        
        # 3. Add Precedence Constraints (within each job)
        # The sub-jobs of a single job must be executed in order.
        # --- YOUR CODE HERE ---
        for j in range(self.jobshop_problem.n_jobs):
            for k in range(1, len(self.jobshop_problem.list_jobs[j])):
                self.model.Add(starts[j][k] >= ends[j][k-1])
        
        
        # 4. Add Resource Constraints (for each machine)
        # A machine can only process one task at a time.
        # (Hint: self.jobshop_problem.job_per_machines is very useful here!)
        # --- YOUR CODE HERE ---
        for machine in self.jobshop_problem.job_per_machines:
            self.model.AddNoOverlap([intervals[x[0]][x[1]]
                                     for x in self.jobshop_problem.job_per_machines[machine]])
        # 5. Define the Makespan and Objective Function
        # The makespan is the completion time of the entire project. We want to minimize it.
        makespan = self.model.NewIntVar(0, horizon, 'makespan')
        # --- YOUR CODE HERE ---
        self.model.AddMaxEquality(makespan, [ends[i][-1] for i in range(len(ends))])
        # TO DO: The makespan is determined by the task that finishes last.
        # Collect all 'end' variables and use model.AddMaxEquality() to link them to the makespan variable.
        self.model.Minimize(makespan)
        
        
        
    def solve(self, **kwargs) -> SolutionJobshop:
        self.init_model(**kwargs)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = kwargs.get("max_time_in_seconds", 10)
        status = solver.Solve(self.model)
        status_human = solver.StatusName(status)
        print(f"Solver finished with status: {status_human}")
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print(f"Makespan: {solver.ObjectiveValue()}")
            # 6. Reconstruct the solution in the required format
            # --- YOUR CODE HERE ---
            # TO DO: Create an empty list for the final schedule.
            # Loop through each job and subjob, just like when you created the variables.
            # For each task, get the solved value of its start and end variables
            # using solver.Value().
            # Append the (start, end) tuple to a list for the current job.
            # After iterating through all subjobs, append the job's schedule to the final schedule list.
            # Finally, return a SolutionJobshop object with your completed schedule.
            
            # Placeholder, replace with your implementation
            reconstructed_schedule = []
            for job in range(len(self.variables["starts"])):
                sch = []
                for subjob in range(len(self.variables["starts"][job])):
                    sch += [(solver.Value(self.variables["starts"][job][subjob]),
                             solver.Value(self.variables["ends"][job][subjob]))]
                reconstructed_schedule += [sch]
            return SolutionJobshop(reconstructed_schedule)
        else:
            print("No solution found.")
            return None