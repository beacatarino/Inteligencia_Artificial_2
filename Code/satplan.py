#!/usr/bin/python

# python libs
import sys
from copy import deepcopy

# user scripts
from general import *

# Class definitions
class Atom:
	def __init__(self, a_name, t_list, n):
		self.name =  a_name
		self.terms_list = t_list
		# False negative, True not negative
		self.negative = n

class Action:
	def __init__(self, ac_name, arg, p_list, e_list):
		self.name = ac_name			# action name
		self.arg_list = arg			# arguments list
		self.precond_list = p_list 	# list of atoms
		self.effect_list = e_list 	# list of atoms

class State:
	def __init__(self, t, a_list):
		self.time = t				# depth of node
		self.atoms_list = a_list 	# list of atoms

# Functions
# Reads an atom string and returns an atom class
def read_atom(atom):

	# splits string in the atom name (before '(') and terms (between '()')
	name = atom[ : atom.find('(') ]
	term_str = atom[ atom.find('(') + 1 : atom.find(')') ]

	# identifies if the atom is negated
	if name[0] == '-':
		negative = False
		name = name[1:]
	else:
		negative =True

	# separates terms in a list
	terms = term_str.split(',')

	return Atom(name, terms, negative)

def read_action_name(action):

	arg_dict = {}

	# splits string in the atom name (before '(') and terms (between '()')
	name = action[ : action.find('(') ]
	arg_str = action[ action.find('(') + 1 : action.find(')') ]

	arg_list = arg_str.split(',')

	n = 0
	for a in arg_list:
		arg_dict[a] = n
		n = n + 1

	return (name, arg_dict)

# Will read generic state line (initial or goal), returning the atom list and
#updating the constant_list
def read_state_line(line, constants_list):
	atoms_list = []

	for a in line[1:]:
		atom = read_atom(a)
		for t in atom.terms_list:
			constants_list.add(t)
		atoms_list.append(atom)

	return atoms_list, constants_list

# fills list of atoms in an action line (preconds and effects)
def fills_act_list(in_list, arg_list):

	out_list = []
	for a in in_list:
		atom = read_atom(a)

		# replaces literals defined in actions arguments with a number
		new_term = []
		for t in atom.terms_list:
			if t in arg_list:
				new_term.append(arg_list.index(t))
			else:
				new_term.append(t)

		atom.terms_list = deepcopy(new_term)
		out_list.append(atom)

	return out_list

def read_data(file_name):

	# Segundo prof, se nao derem I temos de negar tudo ??? <-------------
	initial = None
	actions_list = []
	constants_list = set([])

	with open(file_name) as f:
		for line in f:
			line_terms = line.split()

			# initial state line
			if line[0] == 'I':
				atoms_list, constants_lists = read_state_line(line_terms, \
					constants_list)
				initial = State(0, atoms_list)

			# goal state line
			elif line[0] == 'G':
				atoms_list, constants_lists = read_state_line(line_terms, \
					constants_list)
				goal = State(-1, atoms_list)

			# action line
			elif line[0] == 'A':
				atom = read_atom(line_terms[1])

				arg_list = atom.terms_list
				action_name = atom.name

				# finds point at which the preconds definition ends and the
				#effects definition starts
				n_point = 0
				for term in line_terms:
					if term == '->':
						break
					n_point = n_point + 1

				# ^ dificil de ler sem saber ja a estrutura da linha, mudar
				#depois

				# gets list of precond atoms and effect atoms
				precond_list = fills_act_list(line_terms[3:n_point], arg_list)
				effect_list = fills_act_list(line_terms[n_point+1:], arg_list)

				actions_list.append(Action(action_name, arg_list, \
				precond_list, effect_list))

	return (initial, goal, actions_list, constants_list)


"""
-----------------------------MAIN--------------------------------------
"""
if len(sys.argv) != 2:
	print("Number of arguments is wrong, please enter 1 argument.")
	sys.exit(2)

file_name = sys.argv[1] # input file

(initial, goal, actions_list, constants_list) = read_data(file_name)
# sat_solver(initial,goal,actions_list,constants_list)

general_algorithm(initial, goal, actions_list, constants_list)

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
