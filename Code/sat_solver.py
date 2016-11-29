
"""

#PSEUDO CODE DA P. 96 PARA DPLL CLOSE LEARNING - ITERACTIVE
#ALGORITMO 2.2

def sat_solver_algorithm(CNF_formula):
	b_level = 0

	while True:
		next_branch()
		while True:
			status = deduce_status() 
			if status == conflict:
				analyse_conflict(b_level)
				if b_level == 0:
					return False
				Backtrack(b_level)	
			elif status == SAT:
				return (solution)	
			else:
				break
			
"""


	