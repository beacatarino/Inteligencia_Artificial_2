#!/usr/bin/python

from sat_solver import *
from itertools import combinations_with_replacement,permutations

class SAT_variable:
	def __init__(self,name ,arg,t):
		self.id = name 
		self.arg_list = arg
		self.t = t
	def __eq__(self,other):
		return (isinstance(other,self.__class__)) and other.id == self.id and other.arg_list == self.arg_list and other.t == self.t 

	def __hash__(self):
		return hash(self.id + str(self.arg_list) + str(self.t))

class literal:
	def __init__(self,var,neg): 
		# n = 0 if negated, else n = 1
		self.variable = var
		self.n = neg

class clause:
	def __init__(self,list_variables):
		self.list_variables = list_variables


def create_CNF(initial,goal,actions_list,constants_list,h):

	SAT_variables_list = set([]) # mudar depois para set <-----------------
	atoms_dictionary = {} # Dicionario com nme de atomos e corresponte n de argumentos
	clause_list = []

	# 1 - Initial State --------------------------------------------------------------
	# t = 0:
	for a in initial.atoms_list:
		length = len(a.terms_list)
		atoms_dictionary[a.name] = length

		sat_variable = SAT_variable(a.name,a.terms_list,0)
		SAT_variables_list.add(sat_variable)
		lit = literal(sat_variable,a.negative)
		list_literals = [lit]
		cla = clause(list_literals)
		clause_list.append(cla)

	# other atoms are negated
	for (k,v) in atoms_dictionary.items():
		# Combinacoes possiveis para um atomo
		comb = combinations_with_replacement(constants_list, int(v))
		for c in comb:
			add_clause = True
			permut = permutations(c,int(v))
			for p in permut:
				sat_variable = SAT_variable(k,list(p),0)
				if sat_variable in SAT_variables_list: # atom already exists on the clauses
					add_clause = False
			if add_clause == True:
				sat_variable = SAT_variable(k,list(c),0)			
				SAT_variables_list.add(sat_variable)
				lit = literal(sat_variable,0) # negated
				list_literals = [lit]
				cla = clause(list_literals)
				clause_list.append(cla)


	# 2 - Goal state - final time step of the horizon h

	# 3 - actions imply both their preconditions and their effects, for all time  

	# 4 - frame axioms, stating that, for each ground actions and for each time
	# step , any atom in the Hebrand base not modified by an
	# action maintains the same logical value from t to t + 1

	# 5 - aexactly one action is performed in each time step 


	# Print of clauses
	
	print('-----CLAUSES-----')
	for c in clause_list:
		for l in c.list_variables:
			print(l.variable.id + ' n ' + str(l.n) + '  ' + str(l.variable.arg_list) + ' t= ' + str(l.variable.t))




def general_algorithm(initial,goal,actions_list,constants_list):

	h = 1

	while True:

		SAT_problem = create_CNF(initial,goal,actions_list,constants_list,h)

		"""
		answer = sat_solver_algorithm(SAT_problem)

		if answer != False:
			break
		else:
			h = h + 1	
		"""	
		answer = ''

		if h == 1:
			break
		h = h + 1

	return answer
