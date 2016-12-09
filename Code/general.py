#!/usr/bin/python

import time

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

		print(SAT_problem)
		answer = sat_solver(SAT_problem)
		
		if answer != False:
			print(answer)
			print('------------------------------ANSWER')
			read_answer(SAT_dict,answer,action_keys)
			break
		else:
			print('------------------------------NEXT')
			if h==3:
			 	print('FAILED')
			 	break
			h = h + 1	

	return answer
