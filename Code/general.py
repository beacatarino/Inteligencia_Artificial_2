#!/usr/bin/python

from sat_solver import *
from itertools import product

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

def clause_from_state(atoms_list,clause_list,SAT_variables_list,atoms_dictionary,t):

	for a in atoms_list:
		length = len(a.terms_list)
		atoms_dictionary[a.name] = length

		sat_variable = SAT_variable(a.name,a.terms_list,t)
		SAT_variables_list.add(sat_variable)
		lit = literal(sat_variable,a.negative)
		list_literals = [lit]
		cla = clause(list_literals)
		clause_list.append(cla)

	return (clause_list,SAT_variables_list,atoms_dictionary)

def negated_atoms(atoms_dictionary,constants_list,SAT_variables_list,clause_list,t):

	# other atoms are negated
	for (k,v) in atoms_dictionary.items():
		# Combinacoes possiveis para um atomo
		comb = product(constants_list, repeat = int(v))
		for c in comb:
			sat_variable = SAT_variable(k,list(c),t)
			if sat_variable not in SAT_variables_list:						
				SAT_variables_list.add(sat_variable)
				lit = literal(sat_variable,0) # negated
				list_literals = [lit]
				cla = clause(list_literals)
				clause_list.append(cla)	

	return (SAT_variables_list,clause_list)

def add_action_clause(atoms_list,SAT_variables_list,clause_list,action,c,t):

	for atom in atoms_list:
		arg_list = []
		list_literals = [literal(action,0)] # negated
		for term in atom.terms_list:
			try:
				val = int(term)
				arg_list.append(c[term])					   
			except ValueError:
				arg_list.append(term)
		atom_var = SAT_variable(atom.name,arg_list,t)
		SAT_variables_list.add(atom_var)
		list_literals.append(literal(atom_var,atom.negative))		
		clause_list.append(clause(list_literals))

	return	(SAT_variables_list,clause_list)

def create_CNF(initial,goal,actions_list,constants_list,h):

	SAT_variables_list = set([]) 
	atoms_dictionary = {} # Dicionario com nme de atomos e corresponte n de argumentos
	clause_list = []

	# 1 - Initial State --------------------------------------------------------
	t = 0
	(clause_list,SAT_variables_list,atoms_dictionary) = clause_from_state(initial.atoms_list,clause_list,SAT_variables_list,atoms_dictionary,t)
	(SAT_variables_list,clause_list) = negated_atoms(atoms_dictionary,constants_list,SAT_variables_list,clause_list,t)


	# 2 - Goal state ----------------------------------------------------------
	t = h
	(clause_list,SAT_variables_list,atoms_dictionary) = clause_from_state(goal.atoms_list,clause_list,SAT_variables_list,atoms_dictionary,t)
	(SAT_variables_list,clause_list) = negated_atoms(atoms_dictionary,constants_list,SAT_variables_list,clause_list,t)

	# 3 - actions imply both their preconditions and their effects, for all time  

	for t in range(0, h):
		for a in actions_list:
			print('------------' + a.name)
			combinations = product(constants_list, repeat = len(a.arg_list)) 
			for c in combinations:
				action = SAT_variable(a.name,list(c),t)
				SAT_variables_list.add(action)
				# Add precond list				
				(SAT_variables_list,clause_list) = add_action_clause(a.precond_list,SAT_variables_list,clause_list,action,c,t)	
				# Add effect list
				(SAT_variables_list,clause_list) = add_action_clause(a.effect_list,SAT_variables_list,clause_list,action,c,t+1)	

		 		  
				



	# 4 - frame axioms, stating that, for each ground actions and for each time
	# step , any atom in the Hebrand base not modified by an
	# action maintains the same logical value from t to t + 1

	# 5 - aexactly one action is performed in each time step 


	# Print of clauses
	print('-----CLAUSES-----')
	for c in clause_list:
		print('clause')
		for l in c.list_variables:
			print(' t=' + str(l.variable.t) + ' n=' + str(l.n) + ' ' +l.variable.id + '  ' + str(l.variable.arg_list))
	



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
