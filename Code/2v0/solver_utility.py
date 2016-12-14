from copy import deepcopy

###############################################################################
# Classes definition

# Node class, reflecting the current assignment possibility being explored
class Node:

	def __init__(self, clauses, model, level, parent):
		self.clauses = clauses 		# current clauses for this node
		self.model = model          # after all unit propagations
		self.level = level 			# depth of the current node
		self.parent = parent 		# link to previous node

# Clause class
class Clause:

	def __init__(self, k, term):
		self.id = k 				# clause identifier
		self.term = term 			# list with all literals that compose the
									#clause

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
def find_unit_clause(curr_clause_list, init_clause_list):

	new_assign = {} 			# assignment from unit clause
	learned_from = [] 			# clause that generated assignment
	for clause in curr_clause_list:

		# finds unit clause
		if len(clause.term) == 1:

			# converts to an assignment and
			symb, val = get_symbol(clause.term[0])
			new_assign.update({symb: val})

			# gets clause that originated this unit clause by searching the
			#initial clause
			for f_c in init_clause_list:
				if f_c.id == clause.id:
					orig_clause = deepcopy(f_c.term)
					orig_clause.remove(clause.term[0])
					learned_from.append({clause.term[0]: orig_clause})

					return new_assign, learned_from

	# no unit clause
	return {},[]

# Will remove a clause in clause_list that has a specific identifier
def remove_clause(clause_list, ide):
	for clause in clause_list:
		if clause.id == ide:
			clause_list.remove(clause)
			return clause_list
	return clause_list

# Applies unit propagation from an assignment
def unit_propagation(node, assignment):

	if assignment != {}:

		new_clauses = []

		for clause in node.clauses:
			for symb, val in assignment.items():

				lit = get_literal(symb, val)
				neg_lit = neg(lit)

				# removes clauses with negative of the literal
				if neg_lit in clause.term:
					clause.term.remove(neg_lit)

				# removes clauses with the literal
				if lit not in clause.term:
					new_clauses.append(clause)

		node.clauses = new_clauses

	return node

# searchs the clause list for a conflict and returns its id
def checks_for_conflict(clause_list):

	for clause in clause_list:
		if clause.term == []:
			print("Conflict on term " + str(clause.id))
			return True, clause.id

	return False, None


# def conflict_from_assignment(assign):

	# conflict = []

	# for symb, val in assign.items():
		# conflict.append(get_literal(symb, not val))

	# return conflict


# simplifies the current clause list
def factorize_clauses(clauses):

	# removes duplicates
	unique_clauses = []
	clause_term_list = [clause.term for clause in unique_clauses]
	for c in clauses:
		if c.term not in clause_term_list:
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

def init_clause_list(clauses):

	clause_list = []
	for c in clauses:
		if clause_list != []:
			id_clause = max([clause.id for clause in clause_list])+1
		else:
			id_clause = 0
		clause_list.append(Clause(id_clause, c))

	clause_list = factorize_clauses(clause_list)

	return clause_list
