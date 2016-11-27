import sys

class Atom:
	def __init__(self,a_name,t_list,n):
		self.name =  a_name		
		self.terms_list = t_list
		# 0 negative 1 not negative
		self.negative = n

class Action:
	def __init__(self):
		self.name = ''		
		self.precond_list = [] # list of atoms
		self.effect_list = [] # list of atoms

class State:
	def __init__(self,t,a_list):
		self.time = t
		self.atoms_list = a_list # list of atoms

class Problem:
	def __init__(self,i,g,a_list):
		initial_state = i
		goal_state = g
		actions_list = a_list


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


def read_data(file_name):
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


	#problem = Problem(initial,goal,actions_list)

	return initial



# MAIN

if len(sys.argv) != 2:
    print("Number of arguments is wrong, please enter 1 argument.")
    sys.exit(2)

file_name = sys.argv[1] # input file

initial = read_data(file_name) 

for atom in initial.atoms_list:
	print (atom.name)
