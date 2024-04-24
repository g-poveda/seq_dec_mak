# Welcome

This is an introduction course to scheduling problems and how to solve them using either heuristic or mathematical methods (mainly Constraint programming based).

Main dependencies will be deal by installing the discrete-optimization library to your preferred environment.
```
pip install discrete-optimisation
```

- Introduction course is given in course_material/*.pdf, along with a CheatSheet to use OrtoolsCPSat solver
- Notebooks are then numbered in a logical order.

Good luck ! 
To go further on solving scheduling problems : 
- you can follow the different tutorials/Colab notebooks in https://airbus.github.io/discrete-optimization/master/notebooks.html#introduction-to-rcpsp.
- To improve your skills on CPSat solver : you can go through the extensive examples in the library github repo :
    - https://github.com/google/or-tools/tree/stable/examples/python
    - Go through the full guide : https://developers.google.com/optimization/cp/cp_solver, and notably on the scheduling focused examples (https://developers.google.com/optimization/scheduling)
- If you want to try another solving philosophy : https://www.hexaly.com/docs/last/exampletour/index.html 
 
For further information please contact g-poveda via issues in this repo or if you have his personal contact. 

## Details of the notebook and main take-away 

### Notebook 1 : 
Intro on RCPSP problem + heuristic optimisation :  
- Implementation of SGS algorithm that builds a feasible schedule from a given permutation of tasks.
- [New] : basic greedy local search on the permutation to improve the schedule.

### Notebook 2 : 
CPSat tuto and Jobshop problem.
- CPSat mini tutorial : 
  - create different kind of variables, 
  - explore the expressivity of constraints (boolean, integer, enforcement, global constraints on interval..)
- Generic CPSat encoding of Jobshop problem

### Notebook 3 (no correction given, TP) :
CP solving of RCPSP
- CPSat encoding of RCPSP 
- As bonus, encoding of RCPSP with additional constraints.