#!/usr/bin/python

# user scripts
from sat_solver import *
from encoder import *


def read_answer(SAT_dictionary,answer,action_keys):
	answer = answer[1:]
	terms = answer.split()
	ordered_string = []
	for t in terms:
		if (t[0] != '-') and (int(t) in action_keys):
			for (k,v) in SAT_dictionary.items():
				if int(t) == int(k):
					action = v
					line = str(v.t) + action.id + ' '
					for arg in v.arg_list:
						line += arg + ' '
					#print(line)	
					ordered_string.append(line)

	ordered_string.sort()
	for s in ordered_string:
		print(s[1:])	

def general_algorithm(initial,goal,actions_list,constants_list,atoms_dictionary):

	h = 1

	while True:

		print ('----------------h = ' + str(h))

		SAT_problem,SAT_dict,action_keys = encoder_main(initial,goal,actions_list,constants_list,h,atoms_dictionary)

		"""
		answer = sat_solver_algorithm(SAT_problem)

		if answer != False:
			break
		else:
			h = h + 1	
		"""	
		answer = ''
		if h == 2:
			
			file = open("SAT.txt", "w")
			file.write(SAT_problem)
			file.close()
			
			# answer = 'v -1 -2 -3 -4 -5 -6 7 -8 9 10 11 12 13 14 15 -16 -17 -18 -19 -20 21 -22 23 -24 -25 -26 -27 -28 -29 30 31 32 -33 34 -35 -36 -37 -38 -39 0'
			
			# read_answer(SAT_dict,answer,action_keys)	
			

			break
		h = h + 1

	return answer
