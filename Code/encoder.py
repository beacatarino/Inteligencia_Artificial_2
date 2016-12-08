#!/usr/bin/python

# python libs
from itertools import product, combinations

class SAT_variable:
	def __init__(self,name ,arg,t):
		self.id = name 
		self.arg_list = arg
		self.t = t

	def __eq__(self,other):
		return (isinstance(other,self.__class__)) and other.id == self.id\
		 and other.arg_list == self.arg_list and other.t == self.t 

	def __hash__(self):
		return hash(self.id + str(self.arg_list) + str(self.t))

class literal:
	def __init__(self,var,neg): 
		# n = 0 if negated, else n = 1
		self.variable = var
		self.n = neg

	def __eq__(self,other):
		return(isinstance(other,self.__class__)) and \
		other.variable == self.variable and other.n == self.n

	def __hash__(self):
		return hash(str(self.variable) + str(self.n))	

class clause:
	def __init__(self,list_literals):
		self.list_literals = list_literals

#-----------------------------------------------------------------------
def print_clauses(SAT_var_list,clause_list):
# Help function: apagar depois! <---------------------------------

	f = open("clause.txt", "w")	
	f.write('---------------------------------------SAT variables \n')	
	n = 0
	for v in SAT_var_list: # Print SAT variables
		n = n+1
		f.write(str(n)+' '+str(v.id)+str(v.arg_list)+' t= '+str(v.t)+'\n')
	f.write('\n---------------------------------------CLAUSES \n')	
	n = 0
	for c in clause_list: # Print clauses
		n = n+1
		f.write('c ' + str(n) + ':\n')
		for l in c.list_literals:
			f.write('t=' + str(l.variable.t) + ' n=' + str(l.n) \
			+ ' ' +l.variable.id + '  ' + str(l.variable.arg_list)+'\n')
	f.close()

#-----------------------------------------------------------------------
def clause_from_state(atoms_list,clause_list,SAT_var_list,t):
# Function that given a state and transform it in clauses
# Input: lists of: atoms,clauses,SAT variables;atoms dictionary and time
# Output: lists of: clauses,SAT variables; atoms dictionary
	for a in atoms_list:
		sat_variable = SAT_variable(a.name,a.terms_list,t)
		SAT_var_list.add(sat_variable)
		list_literals = [literal(sat_variable,a.negative)]
		# clause per each atom in the state
		clause_list.append(clause(list_literals))

	return (clause_list,SAT_var_list)

#-----------------------------------------------------------------------
def negated_atoms(atoms_dict,constants_list,\
				SAT_var_list,clause_list,t):
# Function that negates all other atoms in the Hebrand Base
# and transforms it in clauses
# Input: lists of: atoms,clauses,SAT variables;atoms dictionary and time
# Output: lists of: clauses,SAT variables

	# all atoms in the Hebrand Base
	for (k,v) in atoms_dict.items():		
		comb = product(constants_list, repeat = int(v))
		for c in comb: # Possible atom combinations with repetitions
			sat_variable = SAT_variable(k,list(c),t)
			if sat_variable not in SAT_var_list:						
				SAT_var_list.add(sat_variable)
				lit = literal(sat_variable,False) # negated
				list_literals = [lit]
				cla = clause(list_literals)
				clause_list.append(cla)	

	return (SAT_var_list,clause_list)

#-----------------------------------------------------------------------
def check_contradiction(list_atoms,c,t):
# Function that checks if there is a contradiction on the atoms list
# Input: lists of atoms,combination of arguments and time
# Output: True (contraction) or False (no contradiction)
	atoms_list = []
	for atom in list_atoms:
		arg_list = []
		for term in atom.terms_list:
			try:
				val = int(term)
				arg_list.append(c[term])					   
			except ValueError:
				arg_list.append(term)
		sat_variable = 	SAT_variable(atom.name,arg_list,t)				
		if (literal(sat_variable,not atom.negative)) in atoms_list:
			return True
		else:
			atoms_list.append(literal(sat_variable,atom.negative))		

	return False

#-----------------------------------------------------------------------
def add_action_clause(atoms_list,SAT_var_list,clause_list,action,c,t):
# Creates clauses for each atom in one action
# Input: lists of: atoms,SAT variables, clauses; 
#			action,combination of arguments and time
# Output: lists of: clauses,SAT variables

	for atom in atoms_list:
		arg_list = []
		list_literals = [literal(action,False)] # negated
		for term in atom.terms_list:
			try:
				val = int(term)
				arg_list.append(c[term])					   
			except ValueError:
				arg_list.append(term)
		atom_var = SAT_variable(atom.name,arg_list,t)
		SAT_var_list.add(atom_var)
		list_literals.append(literal(atom_var,atom.negative))		
		clause_list.append(clause(list_literals))

	return	(SAT_var_list,clause_list)

#-----------------------------------------------------------------------
def clause_from_frame(a,c,t,constants_list,SAT_var_list,\
						clause_list,atoms_dict):
# Creates clauses for each frame in one action
# Input: lists of: constants,SAT variables, clauses; 
#			action,combination of arguments and time
# Output: lists of: clauses,SAT variables
	atoms_modified = []
	action = SAT_variable(a.name,list(c),t)

	# looking at the effects - which atoms were modified by action
	for atom in a.effect_list: 
		arg_list = []
		for term in atom.terms_list:
			try:
				val = int(term)
				arg_list.append(c[term])					   
			except ValueError:
				arg_list.append(term)
		atom_modified = SAT_variable(atom.name,arg_list,t+1)
		SAT_var_list.add(atom_modified)
		atoms_modified.append(atom_modified)
		length = len(arg_list)

	# 2 clauses for each atom not modified: negated and not negated
	for (k,v) in atoms_dict.items():
		comb = product(constants_list, repeat = int(v))
		for cc in comb:
			list_literals_n = [literal(action,False)]
			list_literals = [literal(action,False)]
			atom = SAT_variable(k,list(cc),t+1)
			SAT_var_list.add(atom)
			if atom not in atoms_modified: 
				sat_variable = SAT_variable(k,list(cc),t)
				SAT_var_list.add(sat_variable)
				list_literals.append(literal(sat_variable,False))
				list_literals.append(literal(atom,True))
				list_literals_n.append(literal(atom,False))
				list_literals_n.append(literal(sat_variable,True))
				clause_list.append(clause(list_literals_n))						
				clause_list.append(clause(list_literals))

	return (SAT_var_list,clause_list)

#-----------------------------------------------------------------------
def create_clauses(initial,goal,actions_list,constants_list,h,atoms_dict):
# Creates clauses for all phases
# Input: initial state, goal state, actions_list from input file,
#		 contants list and the horizon (h)
# Output: lists of: clauses, SAT variables, all actions performed

	SAT_var_list = set([]) # set of variables for this problem
	# atoms_dict: atoms name and respective number of arguments
	clause_list = [] # list of problem clauses 
		
	t = 0 # initial state - all other atoms in the Hebrand base negated
	# If Initial state is not defined, all atoms are negated
	if initial != None: 
		(clause_list,SAT_var_list) = clause_from_state\
		(initial.atoms_list,clause_list,SAT_var_list,t)
	(SAT_var_list,clause_list) = negated_atoms\
	(atoms_dict,constants_list,SAT_var_list,clause_list,t)

	t = h # goal state - final time step of the horizon
	(clause_list,SAT_var_list) = clause_from_state\
	(goal.atoms_list,clause_list,SAT_var_list,t)

	list_all_actions = [] # list of actions for all time steps

	# This cycle performs: action implications, frame axioms and 
	# at-least-one and the at-most-one axioms for each time step
	for t in range(0, h):
		list_actions = [] # list of actions for each time step
		action_literals = []
		for a in actions_list: 		
			contradiction_counter = 0
			# all possible actions given the constants
			combin = product(constants_list, repeat = len(a.arg_list)) 
			for c in combin:
				# if there is an action with contradictions 
				# it won't be created clauses 			
				if (check_contradiction(a.precond_list,c,t) == True) or\
				(check_contradiction(a.effect_list,c,t+1) == True):
					contradiction_counter += 1			
				else:	
					length_before = len(clause_list)
					
					action = SAT_variable(a.name,list(c),t)
					list_actions.append(action)
					list_all_actions.append(action)
					action_literals.append(literal(action,True))					  					
					SAT_var_list.add(action)

					# ACTIONS: imply their precond and their effects
					# Add precond list				
					(SAT_var_list,clause_list) = add_action_clause\
					(a.precond_list,SAT_var_list,clause_list,action,c,t)	
					# Add effect list
					(SAT_var_list,clause_list) = add_action_clause\
					(a.effect_list,SAT_var_list,clause_list,action,c,t+1)	

					# FRAME AXIOMS: any atom in the Hebrand base not 
					# modified by an action maintains the same value					
					SAT_var_list,clause_list = clause_from_frame\
					(a,c,t,constants_list,SAT_var_list,clause_list,atoms_dict)

		# EXACTLY ONE ACTION: is performed in each time step 		
		clause_list.append(clause(action_literals)) # at least one
		for c in combinations(list_actions, 2): # at most one
			list_literals = []
			for l in range(0,2):				
				list_literals.append(literal(c[l],False))
			clause_list.append(clause(list_literals))

	return (SAT_var_list,clause_list,list_all_actions)		

#-----------------------------------------------------------------------
def from_clause_to_SAT(clause_list,SAT_var_list):


	SAT_problem = ''

	# p format variables clauses
	SAT_problem = 'p cnf ' + str(len(SAT_var_list)) + ' ' + str(len(clause_list)) + '\n'

	for c in clause_list:
		for l in c.list_literals:
			n = 0
			for i in SAT_var_list:
				n = n + 1	
				if (i == l.variable):
					break
				
			if l.n == False:
				SAT_problem += '-' + str(n) + ' '
			else:
				SAT_problem += str(n) + ' '

		SAT_problem += '0 '	# end of clause
		#SAT_problem += '\n'

	return SAT_problem



#-----------------------------------------------------------------------
def encoder_main(initial,goal,actions_list,constants_list,h,atoms_dict):

	# creates problem clauses
	(SAT_var_list,clause_list,list_all_actions) = create_clauses\
	(initial,goal,actions_list,constants_list,h,atoms_dict) 
	
	print('number of clauses: '+str(len(clause_list)))
	print_clauses(SAT_var_list,clause_list)		

	SAT_problem = from_clause_to_SAT(clause_list,SAT_var_list)

	SAT_dictionary = {}
	n = 0
	for s in SAT_var_list:
		n = n + 1
		SAT_dictionary[n] = s		

	action_keys = []
	for (k,v) in SAT_dictionary.items():
		if v in list_all_actions:
			action_keys.append(k)

	return SAT_problem, SAT_dictionary,action_keys