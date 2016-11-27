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
	def __init__(self):
		self.time = 0
		self.atoms_list = [] # list of atoms

class Problem:
	def __init__(self):
		initial_state = None
		goal_state = None
		actions_list = []


def read_atom(atom_string):
	"""
	atom_terms = []

	atom_string = atom_string[:-1]
	a_string = atom_string.split('(')

	a_name = a_string[0]
	if a_name[0] == '-': # literal is negative
		negative = 0
		name = a_name[1:]
	else:
		negative = 1
		name = a_name	

	for a in a_string[1:]:
		part = a.split(',')
		for p in part:
			print (p)
			atom_terms.append(p)
	"""

	atoms_terms = []

	atom_string = atom_string[:-1]
	a_string = atom_string.split('(')

	first = a_string[0]
	if first[0] == '-': # literal is negative
		negative = 0
		name = first[1:]
	else:
		negative = 1
		name = first

	for a in a_string[1:]:
		part = a.split(',')
		for p in part:
			atoms_terms.append(p)

	return (name,atoms_terms,negative)		
"""
	print (a)
	atom = Atom()
	atom_terms = []

	line_par = a.split('(')

	print (line_par)

	for par in line_par[:]:
		print(par)

	atom.name = line_par[0]
	print('name:' + atom.name)

	line_term = line_par[1]
	line_term = line_term[:-1] #remove last ')'
	line_term = line_term.split(',')

	for term in line_term: #find terms
		print('term:' + term)
		atom_terms.append(term)       		

	atom.terms_list = atom_terms
"""


def read_data(file_name):

	problem = Problem()
	initial = None #Se nao houver initial -negar atomos <-- do it later

	with open(file_name) as f:
		for line in f:
			# removes '\n' character
			#line = line.rstrip()
	        # splits every word in the line separated by whitespace
			line_list = line.split()      

			if line[0] == 'I':
				initial = State()
				initial.time = 0
				a_list = []				

				for a in line_list[1:]:
					(name,atom_terms,negative) = read_atom(a)
	        			
	        		a_list.append(Atom(name,atom_terms,negative))

				initial.atoms_list = a_list 	

				for atom in a_list:
					print ('atom: ' + atom.name)
					for p in atom.terms_list:
						print p

			elif line[0] == 'A':
				print ('action')

			elif line[0] == 'G':
				print ('Goal')


	if initial != None:    	
	    problem.initial_state = initial	

	return a_list

# MAIN

if len(sys.argv) != 2:
    print("Number of arguments is wrong, please enter 1 argument.")
    sys.exit(2)

file_name = sys.argv[1] # input file

atom_list = read_data(file_name) 

for atom in atom_list:
	print (atom.name)