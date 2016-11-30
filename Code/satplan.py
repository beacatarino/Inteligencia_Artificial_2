#!/usr/bin/python

from general import *

import sys

class Atom:
	def __init__(self,a_name,t_list,n):
		self.name =  a_name		
		self.terms_list = t_list
		# 0 negative 1 not negative
		self.negative = n

class Action:
	def __init__(self,ac_name,arg,p_list,e_list):
		self.name = ac_name	# action name 
		self.arg_list = arg # arguments list	
		self.precond_list = p_list # list of atoms
		self.effect_list = e_list # list of atoms

class State:
	def __init__(self,t,a_list):
		self.time = t
		self.atoms_list = a_list # list of atoms


def read_atom(atom):
	terms_list = []
	atom = atom[:-1]

	part = atom.split('(')

	first_part = part[0]
	
	if first_part[0] == '-':
		negative = 0
		name = first_part[1:]
	else:
		negative = 1
		name = first_part	

	terms_part = part[1]	
	terms = terms_part.split(',')

	for term in terms:
		terms_list.append(term)

	return (name,terms_list,negative)

def read_action_name(action):
	arg_dict = {}
	action = action[:-1]
	n = 0

	part = action.split('(')

	name = part[0]

	arg_part = part[1]

	arg = arg_part.split(',')

	for a in arg:
		arg_dict[a] = n
		n = n + 1

	return (name,arg_dict)


def read_data(file_name):

	# Sedundo prof, se nao derem I temos de negar tudo ??? <-------------
	initial = None
	actions_list = []
	constants_list = set([])

	with open(file_name) as f:
		for line in f:
			line_terms = line.split()

			if line[0] == 'I':
				atoms_list = []

				for a in line_terms[1:]:
					(name,terms_list,negative) = read_atom(a)
					for t in terms_list:
						constants_list.add(t)
					atoms_list.append(Atom(name,terms_list,negative))


				initial = State(0,atoms_list)

			elif line[0] == 'G':
				atoms_list = []
				for a in line_terms[1:]:
					(name,terms_list,negative) = read_atom(a)
					for t in terms_list:
						constants_list.add(t)
					atoms_list.append(Atom(name,terms_list,negative))
				goal = State(-1,atoms_list)	

			elif line[0] == 'A':
					(action_name,arg_dict) = read_action_name(line_terms[1])

					arg_list = []
					for k,v in arg_dict.items():
						arg_list.append(v)

					n_point = 0
					for term in line_terms:
						if term == '->':
							break
						n_point = n_point + 1	


					precond_list = []
					for a in line_terms[3:n_point]:
						(name,terms_list,negative) = read_atom(a)
						new_term = []
						for t in terms_list:
							if arg_dict.has_key(t):
								new_term.append(arg_dict[t])
							else:
								new_term.append(t)

						precond_list.append(Atom(name,new_term,negative))
					
					effect_list = []
					for a in line_terms[n_point+1:]:
						(name,terms_list,negative) = read_atom(a)
						new_term = []
						for t in terms_list:
							if arg_dict.has_key(t):
								new_term.append(arg_dict[t])
							else:
								new_term.append(t)
						effect_list.append(Atom(name,new_term,negative))

					
					actions_list.append(Action(action_name,arg_list,precond_list,effect_list))		

	return (initial,goal,actions_list,constants_list)


"""
-----------------------------MAIN--------------------------------------
"""
if len(sys.argv) != 2:
    print("Number of arguments is wrong, please enter 1 argument.")
    sys.exit(2)

file_name = sys.argv[1] # input file
 
(initial,goal,actions_list,constants_list) = read_data(file_name)
# sat_solver(initial,goal,actions_list,constants_list) 

general_algorithm(initial,goal,actions_list,constants_list)


"""
# PRINTS  
print ('--Initial State')
for a in initial.atoms_list:
	print (a.name + str(a.terms_list))


print ('--Goal State')
for a in goal.atoms_list:
	print (a.name + str(a.terms_list))

print('--Actions')		
for a in actions_list:
	print(a.name)

print('--Constants')	
for c in constants_list:
	print(c)
"""
