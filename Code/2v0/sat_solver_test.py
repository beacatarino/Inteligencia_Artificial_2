import os
import sys
import time

from sat_solver import sat_solver

cnf_path = sys.argv[1]
cnf_name = os.path.basename(cnf_path)

with open(cnf_path,'r') as cnf:

	start_time = time.time()

	sol = sat_solver(cnf, verbose = True)

	if not sol and 'uuf' in cnf_name:
		print('Correct!')
	elif sol and not 'uuf' in cnf_name:
		print('Correct!')
	else:
		print('Incorrect!')

time = time.time() - start_time
secs = time%60
mins = (time//60)%60
hours = mins//60

print("--- time: %2.0fh %2.0fm %2.9f s  ---" % (hours, mins, secs))
