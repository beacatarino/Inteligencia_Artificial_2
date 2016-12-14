from copy import deepcopy

class Node:

	def __init__(self, clauses, symbols, model, level, parent):
		self.clauses = clauses 		# clauses in current iteration
		self.symbols = symbols 		# list of symbols
		self.model = model          # after all unit propagations
		self.level = level
		self.parent = parent

# identifies each clause term with an integer id
class Clause_term:

	def __init__(self, k, term):
		self.id = k
		self.term = term

class Assign_term:

	def __init__(self, k, boolean, level):
		self.id = k
		self.value = boolean
		self.l = level

	def __eq__(self,other):
		return (isinstance(other, self.__class__)) and other.id == self.id\
			and other.value == self.value and other.l == self.l

	def __hash__(self):
		return hash(self.id + str(self.value) + str(self.l))

# Computes the symbol and value of a literal
def get_symbol(literal):

	if literal[0] == '-':
		return literal[1:], False
	else:
		return literal, True

# Will get a literal from a symbol and its boolean value, i.e. ('1', False)
#to '-1'
def get_literal(symb, val):

	if val:
		return symb
	else:
		return '-' + symb

# Returns the negative of the symbol
def neg(literal):

	if literal[0] == '-':
		return literal[1:]
	else:
		return '-' + literal

# Searches the current clause list for a unit clauses and assigns them to its
#correct. Will also find a clause that originated the assignment.
def find_unit_clause(clause_list, model, full_clause_list):

	new_assign = {} 			# assignment from unit clause
	learned_from = [] 			# clause that generated assignment
	for clause in clause_list:

		# finds unit clause
		if len(clause.term) == 1:
			symb, val = get_symbol(clause.term[0])
			new_assign.update({symb: val})

			# gets clause that originated this unit clause by searching the
			#initial clause
			for f_c in full_clause_list:
				if f_c.id == clause.id and clause.term[0] in f_c.term:
					orig_clause = deepcopy(f_c.term)
					orig_clause.remove(clause.term[0])
					learned_from.append({clause.term[0]:orig_clause})

					return new_assign, learned_from

	# no unit clause
	return {},[]

def unit_propagation(node, unit_dict):

	# propagates the unit clause

	# removes clauses with the literal
	new_clauses = deepcopy(node.clauses)
	new_terms = [c.term for c in new_clauses]
	for symb, val in unit_dict.items():
		for clause in node.clauses:
			if get_literal(symb, val) in clause.term and clause.term in new_terms:
				for c in new_clauses:
					if c.term == clause.term:
						new_clauses.remove(c)

	node.clauses = new_clauses

	# removes clauses with negative of the literal
	for symb, val in unit_dict.items():
		for clause in node.clauses:
			neg_lit = neg(get_literal(symb, val))
			if neg_lit in clause.term:
				clause.term.remove(neg_lit)

	return node

# searchs the clause list for a conflict and returns its id
def checks_for_conflict(clause_list):

	for clause in clause_list:
		if clause.term == []:
			return True, clause.id

	return False, None

def conflict_from_assignment(assign):

	conflict = []

	for symb, val in assign.items():
		conflict.append(get_literal(symb, not val))

	return conflict

# simplifies the current clause list
def factorize_clauses(clauses):

	# removes duplicates
	unique_clauses = []
	term_list = [clause.term for clause in unique_clauses]
	for c in clauses:
		if c.term not in term_list:
			unique_clauses.append(c)

	new_clauses = deepcopy(unique_clauses)

	for ci in unique_clauses:
		if not implied(ci, unique_clauses):
			# if at least on literal is not in a different clause, the
			#the two clauses dont imply each other
			new_clauses.remove(ci)


	return new_clauses

# checks test is implied by another clause
def implied(test, clause_list):
	for clause in clause_list:
		implied = True
		for t in test.term:
			if t not in clause.term:
				implied = False

		if implied:
			return True
	return False

# initializes the intial clause list
def init_clause_list(clauses):
	clause_list = []
	for c in clauses:
		if clause_list != []:
			id_clause = max([clause.id for clause in clause_list])+1
		else:
			id_clause = 0
		clause_list.append(Clause_term(id_clause, c))

	return clause_list

def add_learned_clause(node, clause_list, learned_clause):
	# adds learned_clause
	n = node
	if learned_clause != None:
		if n.clauses != []:
			id_clause = max([clause.id for clause in n.clauses])+1
		else:
			id_clause = 0
		n.clauses.append(Clause_term(id_clause, learned_clause))

		if clause_list != []:
			id_clause = max([clause.id for clause in clause_list])+1
		else:
			id_clause = 0
		clause_list.append(Clause_term(id_clause, learned_clause))

	return clause_list
