import os
import sys

from sat_solver import sat_solver

cnf_path = sys.argv[1]
cnf_name = os.path.basename(cnf_path)

with open(cnf_path,'r') as cnf:
        
    sol = sat_solver(cnf, verbose = True)

    if not sol and 'uuf' in cnf_name:
        print('Correct!')
    elif sol and not 'uuf' in cnf_name:
        print('Correct!')
    else:
        print('Incorrect!')
