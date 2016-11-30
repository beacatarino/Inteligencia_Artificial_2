#!/usr/bin/python

from sat_solver import *
from itertools import product, combinations

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

def from_clause_to_SAT(clause_list,SAT_variables_list):

	SAT_problem = ''

	# p format variables clauses
	SAT_problem = 'p cnf ' + str(len(SAT_variables_list)) + ' ' + str(len(clause_list)) + ' '

	for c in clause_list:
		for l in c.list_variables:
			n = 0
			for i in SAT_variables_list:
				n = n + 1	
				if (i == l.variable):
					break
				
			if l.n == 0:
				SAT_problem += '-' + str(n) + ' '
			else:
				SAT_problem += str(n) + ' '

		SAT_problem += '0 '	# end of clause
		#SAT_problem += '\n'

	print(SAT_problem)

	return SAT_problem


def create_CNF(initial,goal,actions_list,constants_list,h):

	SAT_variables_list = set([]) 
	atoms_dictionary = {} # Dicionario com nme de atomos e corresponte n de argumentos
	clause_list = []
	

	# 1 - Initial State --------------------------------------------------------
	t = 0
	(clause_list,SAT_variables_list,atoms_dictionary) = clause_from_state(initial.atoms_list,clause_list,SAT_variables_list,atoms_dictionary,t)
	(SAT_variables_list,clause_list) = negated_atoms(atoms_dictionary,constants_list,SAT_variables_list,clause_list,t)

	print('inicio ' + str(len(clause_list))	)

	# 2 - Goal state ----------------------------------------------------------
	t = h
	(clause_list,SAT_variables_list,atoms_dictionary) = clause_from_state(goal.atoms_list,clause_list,SAT_variables_list,atoms_dictionary,t)
	(SAT_variables_list,clause_list) = negated_atoms(atoms_dictionary,constants_list,SAT_variables_list,clause_list,t)

	print('after goal ' + str(len(clause_list))	)

	# 3 - actions imply both their preconditions and their effects, for all time  

	for t in range(0, h):
		list_actions = []
		action_literals = []
		for a in actions_list:
			#print('------------' + a.name)
			combin = product(constants_list, repeat = len(a.arg_list)) 
			for c in combin:
				action = SAT_variable(a.name,list(c),t)
				list_actions.append(action)
				action_literals.append(literal(action,1))
				SAT_variables_list.add(action)
				# Add precond list				
				(SAT_variables_list,clause_list) = add_action_clause(a.precond_list,SAT_variables_list,clause_list,action,c,t)	
				# Add effect list
				(SAT_variables_list,clause_list) = add_action_clause(a.effect_list,SAT_variables_list,clause_list,action,c,t+1)	
		
		print('after actions ' + str(len(clause_list)))

		# 5 - exactly one action is performed in each time step 
		clause_list.append(clause(action_literals)) # clause at least one

		print('after at least one ' + str(len(clause_list)))

		# Clauses At most one:	
		for c in combinations(list_actions, 2):
			list_literals = []
			for l in range(0,2):
				list_literals.append(literal(c[l],0))
			clause_list.append(clause(list_literals))	

	print('after at most one ' + str(len(clause_list)))
	


	# 4 - frame axioms - any atom in the Hebrand base not modified by an action 
	#	   maintains the same logical value from t to t + 1

	# MISSING: COMO saber que um atomo nao e modificado. Olhamos para os precons, effects ou apenas variaveis?
	# De resto, para cada atomo e so aplicar as clausulas como tenho nas notas	

	"""
	for t in range(0,h):
		for a in list_actions: # all possible combinations for l actions
			combinations = product(constants_list, repeat = len(a.arg_list)) 
			for c in combinations:
	"""			


	print('after frame ' + str(len(clause_list)))	

	

	


	"""
	# Print of clauses
	print('-----CLAUSES-----')
	n = 0
	for c in clause_list:
		n = n+1
		for l in c.list_variables:
			print('clause ' + str(n) + ' t=' + str(l.variable.t) + ' n=' + str(l.n) + ' ' +l.variable.id + '  ' + str(l.variable.arg_list))
	"""

	SAT_problem = from_clause_to_SAT(clause_list,SAT_variables_list)

	return SAT_problem



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
