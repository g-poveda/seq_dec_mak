import logging
import os

import pandas as pd

from discrete_optimization.generic_tools.callbacks.loggers import NbIterationTracker
from discrete_optimization.generic_tools.callbacks.stats_retrievers import (
    BasicStatsCallback,
    StatsWithBoundsCallback,
)
from discrete_optimization.generic_tools.cp_tools import ParametersCp
from discrete_optimization.generic_tools.do_solver import StatusSolver
from discrete_optimization.generic_tools.study import (
    Experiment,
    Hdf5Database,
    SolverConfig,
)
from discrete_optimization.jsp.parser import get_data_available, parse_file
from discrete_optimization.jsp.solvers.cpsat import CpSatJspSolver
from discrete_optimization.jsp.solvers.dp import DpJspSolver

logging.basicConfig(level=logging.INFO)

study_name = "jsp-study-0"
overwrite = True  # do we overwrite previous study with same name or not? if False, we possibly add duplicates
instances = [os.path.basename(p) for p in get_data_available()][:10]
p = ParametersCp.default_cpsat()
p.nb_process = 10
solver_configs = {
    "cpsat-1proc": SolverConfig(
        cls=CpSatJspSolver,
        kwargs=dict(
            time_limit=5,
            parameters_cp=ParametersCp.default(),
        ),
    ),
    "cpsat-multiproc": SolverConfig(
        cls=CpSatJspSolver,
        kwargs=dict(
            time_limit=5,
            parameters_cp=p,
        ),
    ),
    "dp": SolverConfig(
        cls=DpJspSolver,
        kwargs={"time_limit":5}
    )
}

database_filepath = f"{study_name}.h5"
if overwrite:
    try:
        os.remove(database_filepath)
    except FileNotFoundError:
        pass

# loop over instances x configs
for instance in instances:
    for config_name, solver_config in solver_configs.items():

        logging.info(f"###### Instance {instance}, config {config_name} ######\n\n")

        try:
            # init problem
            file = [f for f in get_data_available() if instance in f][0]
            problem = parse_file(file)
            # init solver
            stats_cb = StatsWithBoundsCallback()
            if config_name in {"dp"}:
                stats_cb = BasicStatsCallback()
            solver = solver_config.cls(problem, **solver_config.kwargs)
            solver.init_model(**solver_config.kwargs)
            # solve
            result_store = solver.solve(
                callbacks=[
                    stats_cb,
                    NbIterationTracker(step_verbosity_level=logging.INFO),
                ],
                **solver_config.kwargs,
            )
        except Exception as e:
            # failed experiment
            metrics = pd.DataFrame([])
            status = StatusSolver.ERROR
            reason = f"{type(e)}: {str(e)}"
        else:
            # get metrics and solver status
            status = solver.status_solver
            metrics = stats_cb.get_df_metrics()
            reason = ""

        # store corresponding experiment
        with Hdf5Database(
            database_filepath
        ) as database:  # ensure closing the database at the end of computation (even if error)
            xp_id = database.get_new_experiment_id()
            xp = Experiment.from_solver_config(
                xp_id=xp_id,
                instance=instance,
                config_name=config_name,
                solver_config=solver_config,
                metrics=metrics,
                status=status,
                reason=reason,
            )
            database.store(xp)
