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

	def __eq__(self,other):
		return(isinstance(other,self.__class__)) and other.variable == self.variable and other.n == self.n

	def __hash__(self):
		return hash(str(self.variable) + str(self.n))	

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
				lit = literal(sat_variable,False) # negated
				list_literals = [lit]
				cla = clause(list_literals)
				clause_list.append(cla)	

	return (SAT_variables_list,clause_list)

def add_action_clause(atoms_list,SAT_variables_list,clause_list,action,c,t):

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
		SAT_variables_list.add(atom_var)
		list_literals.append(literal(atom_var,atom.negative))		
		clause_list.append(clause(list_literals))

	return	(SAT_variables_list,clause_list)

def check_contradiction(action,c,t):
	#print('-------------' + action.name + str(c))

	atoms_list = []
	for atom in action.precond_list:
		arg_list = []
		for term in atom.terms_list:
			try:
				val = int(term)
				arg_list.append(c[term])					   
			except ValueError:
				arg_list.append(term)	
		#print(atom.name + str(arg_list) + str(atom.negative))			
		if (literal(SAT_variable(atom.name,arg_list,t),not atom.negative)) in atoms_list:
			#print('contradiction!')	
			#print(atom.name + str(arg_list) + str(not atom.negative))
			#print(atom.name + str(arg_list) + str(atom.negative))
			return True
		else:
			atoms_list.append(literal(SAT_variable(atom.name,arg_list,t),atom.negative))

	atoms_list = []
	for atom in action.effect_list:
		arg_list = []
		for term in atom.terms_list:
			try:
				val = int(term)
				arg_list.append(c[term])					   
			except ValueError:
				arg_list.append(term)	
		#print(atom.name + str(arg_list) + str(atom.negative))			
		if (literal(SAT_variable(atom.name,arg_list,t+1),not atom.negative)) in atoms_list:
			#print('contradiction!')		
			#print(atom.name + str(arg_list) + str(not atom.negative))
			#print(atom.name + str(arg_list) + str(atom.negative))
			return True
		else:
			atoms_list.append(literal(SAT_variable(atom.name,arg_list,t+1),atom.negative))				

	return False

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
				
			if l.n == False:
				SAT_problem += '-' + str(n) + ' '
			else:
				SAT_problem += str(n) + ' '

		SAT_problem += '0 '	# end of clause
		#SAT_problem += '\n'

	#print(SAT_problem)

	return SAT_problem

def read_answer(SAT_dictionary,answer,action_keys):
	terms = answer.split()
	for t in terms:
		if (t[0] != '-') and (int(t) in action_keys):
			for (k,v) in SAT_dictionary.items():
				if int(t) == int(k):
					action = v
					str = action.id + ' '
					for arg in v.arg_list:
						str += arg + ' '
					print(str)
			

	


def create_CNF(initial,goal,actions_list,constants_list,h):

	SAT_variables_list = set([]) 
	atoms_dictionary = {} # Dicionario com nme de atomos e corresponte n de argumentos
	clause_list = []
	

	# 1 - Initial State --------------------------------------------------------
	t = 0
	(clause_list,SAT_variables_list,atoms_dictionary) = clause_from_state(initial.atoms_list,clause_list,SAT_variables_list,atoms_dictionary,t)
	(SAT_variables_list,clause_list) = negated_atoms(atoms_dictionary,constants_list,SAT_variables_list,clause_list,t)

	#print('inicio ' + str(len(clause_list))	)

	# 2 - Goal state ----------------------------------------------------------
	t = h
	(clause_list,SAT_variables_list,atoms_dictionary) = clause_from_state(goal.atoms_list,clause_list,SAT_variables_list,atoms_dictionary,t)
	#(SAT_variables_list,clause_list) = negated_atoms(atoms_dictionary,constants_list,SAT_variables_list,clause_list,t)

	print('after goal ' + str(len(clause_list))	)


	action_counter = 0
	
	frame_counter = 0
	action_5 = 0

	list_all_actions = []

	for t in range(0, h):
		list_actions = []
		action_literals = []
		for a in actions_list:			
			contradiction_counter = 0
			combin = product(constants_list, repeat = len(a.arg_list)) 
			for c in combin:
				#print('------------' + a.name + str(c))
				if (check_contradiction(a,c,t) == True): # there is a contradiction
					"""
					action = SAT_variable(a.name,list(c),t)
					SAT_variables_list.add(action)
					list_literals = [literal(action,False)]
					clause_list.append(clause(list_literals))
					
					"""			
					#print('contradiction ' + a.name + str(c))
					contradiction_counter += 1			
				else:	
					length_before = len(clause_list)
					# 3 - actions imply both their preconditions and their effects, for all time   
					action = SAT_variable(a.name,list(c),t)
					list_actions.append(action)
					list_all_actions.append(action)
					action_literals.append(literal(action,True))
					SAT_variables_list.add(action)
					# Add precond list				
					(SAT_variables_list,clause_list) = add_action_clause(a.precond_list,SAT_variables_list,clause_list,action,c,t)	
					# Add effect list
					(SAT_variables_list,clause_list) = add_action_clause(a.effect_list,SAT_variables_list,clause_list,action,c,t+1)	
					action_counter = action_counter + len(clause_list) - length_before

					# 4 - frame axioms - any atom in the Hebrand base not modified by an action 
					#	   maintains the same logical value from t to t + 1
					atoms_modified = []
					atoms_dictionary = {}	

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
						SAT_variables_list.add(atom_modified)
						atoms_modified.append(atom_modified)
						length = len(arg_list)
						atoms_dictionary[atom.name] = length

					for (k,v) in atoms_dictionary.items():
						comb = product(constants_list, repeat = int(v))
						for cc in comb:
							list_literals_n = [literal(action,False)]
							list_literals = [literal(action,False)]
							atom = SAT_variable(k,list(cc),t+1)
							SAT_variables_list.add(atom)
							if atom not in atoms_modified: # Add 2 clauses
								list_literals.append(literal(atom,True))
								list_literals.append(literal(SAT_variable(k,list(cc),t),False))
								SAT_variables_list.add(SAT_variable(k,list(cc),t))
								list_literals_n.append(literal(atom,False))
								list_literals_n.append(literal(SAT_variable(k,list(cc),t),True))
								clause_list.append(clause(list_literals_n))						
								clause_list.append(clause(list_literals))
								frame_counter = frame_counter + 2	

			#print('contradiction: ' + str(contradiction_counter))

		# 5 - exactly one action is performed in each time step 
		clause_list.append(clause(action_literals)) # clause at least one		
		action_5 += 1
		# 	- Clauses At most one:

		for c in combinations(list_actions, 2):
			list_literals = []
			for l in range(0,2):				
				list_literals.append(literal(c[l],False))
			clause_list.append(clause(list_literals))
			action_5 +=1

		

	print('3 actions  ' + str(action_counter) + ' contradictions ' + str(contradiction_counter))
	print('frame counter ' + str(frame_counter))
	print('action 5: ' + str(action_5))
	print('final: '+str(len(clause_list)))


	"""
	# print('after frame ' + str(len(clause_list)))	

	"""
	n = 0
	for v in SAT_variables_list:
		n = n+1
		print(str(n) + ' '+ str(v.id) + str(v.arg_list) + ' t= ' + str(v.t))
	
	
	
	# Print of clauses

	file = open("clause.txt", "w")
	
	#print('-----CLAUSES-----')
	n = 0
	for c in clause_list:
		n = n+1
		file.write('c ' + str(n) + ':\n')
		for l in c.list_variables:
			file.write('t=' + str(l.variable.t) + ' n=' + str(l.n) + ' ' +l.variable.id + '  ' + str(l.variable.arg_list)+'\n')
	
	file.close()	
	
	SAT_problem = from_clause_to_SAT(clause_list,SAT_variables_list)

	SAT_dictionary = {}
	n = 0
	for s in SAT_variables_list:
		n = n + 1
		SAT_dictionary[n] = s		

	action_keys = []
	for (k,v) in SAT_dictionary.items():
		if v in list_all_actions:
			action_keys.append(k)
			#print(k)

	return SAT_problem, SAT_dictionary,action_keys



def general_algorithm(initial,goal,actions_list,constants_list):

	h = 1

	while True:
		print ('----------------h = ' + str(h))

		SAT_problem,SAT_dictionary,action_keys = create_CNF(initial,goal,actions_list,constants_list,h)

		"""
		answer = sat_solver_algorithm(SAT_problem)

		if answer != False:
			break
		else:
			h = h + 1	
		"""	
		answer = ''
		
		if h == 3:
			
			#print(SAT_problem)			
			file = open("SAT.txt", "w")

			file.write(SAT_problem)
			file.close()

			
			answer = 'v -1 -2 -3 -4 -5 -6 -7 8 -9 -10 -11 -12 -13 14 -15 16 17 -18 -19 -20 -21 -22 -23 -24 -25 -26 -27 -28 -29 -30 31 32 -33 -34 -35 -36 -37 -38 -39 40 -41 -42 -43 -44 -45 -46 -47 -48 -49 -50 -51 -52 -53 -54 -55 -56 -57 -58 -59 -60 -61 -62 -63 -64 -65 -66 -67 -68 -69 -70 71 -72 -73 -74 -75 -76 -77 -78 79 -80 -81 -82 -83 -84 -85 -86 -87 -88 -89 -90 -91 -92 -93 -94 -95 96 97 98 -99 -100 -101 -102 -103 -104 -105 -106 -107 -108 -109 -110 -111 -112 -113 -114 -115 -116 -117 -118 -119 -120 -121 -122 -123 -124 -125 -126 -127 -128 -129 130 131 -132 -133 -134 -135 -136 137 -138 -139 -140 -141 -142 -143 -144 -145 -146 -147 -148 -149 -150 -151 -152 -153 -154 -155 -156 -157 -158 -159 -160 -161 -162 163 164 -165 -166 -167 -168 -169 -170 -171 -172 -173 -174 -175 -176 -177 -178 -179 -180 -181 -182 -183 -184 -185 -186 -187 -188 -189 -190 -191 -192 -193 -194 -195 -196 -197 -198 -199 -200 -201 -202 -203 204 -205 -206 -207 -208 -209 -210 211 -212 -213 -214 -215 -216 -217 -218 -219 -220 -221 -222 -223 -224 -225 -226 -227 -228 -229 -230 -231 -232 -233 -234 235 236 -237 -238 239 -240 -241 -242 -243 -244 -245 -246 -247 -248 -249 -250 -251 -252 -253 -254 -255 -256 -257 -258 -259 -260 0'
			
			read_answer(SAT_dictionary,answer[1:],action_keys)	
			

			break
		h = h + 1



	return answer
