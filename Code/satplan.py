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
	arg_list = []
	action = action[:-1]

	part = action.split('(')

	name = part[0]

	arg_part = part[1]

	arg = arg_part.split(',')

	for a in arg:
		arg_list.append(a)

	return (name,arg_list)


def read_data(file_name):

	# Sedundo prof, se nao derem I temos de negar tudo ??? <-------------
	initial = None
	actions_list = []

	with open(file_name) as f:
		for line in f:
			line_terms = line.split()

			if line[0] == 'I':
				atoms_list = []

				for a in line_terms[1:]:
					(name,terms_list,negative) = read_atom(a)
					atoms_list.append(Atom(name,terms_list,negative))


				initial = State(0,atoms_list)

			elif line[0] == 'G':
				atoms_list = []
				for a in line_terms[1:]:
					(name,terms_list,negative) = read_atom(a)
					atoms_list.append(Atom(name,terms_list,negative))
				goal = State(-1,atoms_list)	

			elif line[0] == 'A':
					(action_name,arg_list) = read_action_name(line_terms[1])

					n_point = 0
					for term in line_terms:
						if term == '->':
							break
						n_point = n_point + 1	

					precond_list = []
					for a in line_terms[3:n_point-1]:
						(name,terms_list,negative) = read_atom(a)
						precond_list.append(Atom(name,terms_list,negative))

					effect_list = []
					for a in line_terms[n_point+1:]:
						(name,terms_list,negative) = read_atom(a)
						effect_list.append(Atom(name,terms_list,negative))

					
					actions_list.append(Action(action_name,arg_list,precond_list,effect_list))		

	return (initial,goal,actions_list)

"""
-----------------------------MAIN--------------------------------------
"""
if len(sys.argv) != 2:
    print("Number of arguments is wrong, please enter 1 argument.")
    sys.exit(2)

file_name = sys.argv[1] # input file
 
(initial,goal,actions_list) = read_data(file_name) 

print ('--Initial State')
for a in initial.atoms_list:
	print (a.name + str(a.terms_list))

print ('--Goal State')
for a in goal.atoms_list:
	print (a.name + str(a.terms_list))

print('--Actions')		
for a in actions_list:
	print(a.name)