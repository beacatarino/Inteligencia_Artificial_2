from copy import deepcopy

class Node:

	def __init__(self, clauses, symbols, model, level, parent):
		self.clauses = clauses
		self.symbols = symbols
		self.model = model          # after all unit propagations
		self.level = level
		self.parent = parent

class Clause_term:

	def __init__(self, k, term):
		self.id = k
		self.sat = False
		self.res = False
		self.unit = False
		self.unit_term = None
		self.term = term
		self.watched = []
		self.nxt_lit = 0
		self.term_len = len(term)

		# checks if clause is already unsat or unit
		if self.term_len == 0:
			self.res = True
		elif self.term_len == 1:
			self.unit = True
			self.unit_term = self.term[0]
		else:
			# initializes watched literals
			self.watched = self.term[0:2]
			self.nxt_lit = 2

	def assign(self, lit):
		if self.unit:
			if lit == self.unit_term:
				self.res = True
				self.sat = True
			if neg(lit) == self.unit_term:
				self.res = True
		else:
			self.assign_watched(lit)

	def assign_watched(self, lit):
		if lit in self.watched:
			self.res = True
			self.sat = True
		if neg(lit) in self.watched:
			if neg(lit) == self.watched[0]:
				if self.nxt_lit == self.term_len:
					self.unit_term = self.watched[1]
					self.unit = True
				else:
					self.swap(0)
			elif neg(lit) == self.watched[1]:
				if self.nxt_lit == self.term_len:
					self.unit_term = self.watched[0]
					self.unit = True
				else:
					self.swap(1)

	# num is index of watched
	def swap(self, num):
		self.watched[num] = self.term[self.nxt_lit]
		self.nxt_lit += 1

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
def find_unit_clause(node):

	new_assign = {} 			# assignment from unit clause
	learned_from = [] 			# clause that generated assignment
	for clause in node.clauses:

		# finds unit clause
		if clause.unit and not clause.res:
			# converts to an assignment and
			symb, val = get_symbol(clause.unit_term)

			return new_assign, []

	# no unit clause
	return {},[]

def check_sat(clauses):
	for c in clauses:
		if not c.res:
			return False
		elif not c.sat:
			return False
	return True

def unit_propagation(node, unit_dict):

	node.model.update(unit_dict)

	# propagates the unit clause

	for symb, val in unit_dict.items():
		lit = get_literal(symb, val)
		for clause in node.clauses:
			if not clause.res:
				clause.assign(lit)

	# print('After removing false clauses: \n' + str(node.clauses))

	return node

def checks_for_conflict(clause_list):

	for clause in clause_list:
		if clause.res and not clause.sat:
			#print("Conflict on term " + str(clause.id) + ": " + str(clause.term))
			return True, clause.id

	return False, None

def conflict_from_assignment(assign):

	conflict = []

	for symb, val in assign.items():
		conflict.append(get_literal(symb, not val))

	return conflict

def factorize_clauses(clauses):

	# removes duplicates
	unique_clauses = []
	clause_terms = [clause.term for clause in unique_clauses]
	for c in clauses:
		if c.term not in clause_terms:
			unique_clauses.append(c)

	new_clauses = deepcopy(unique_clauses)

	for ci in unique_clauses:
		if not implied(ci, unique_clauses):
			# if at least on literal is not in a different clause, the
			#the two clauses dont imply each other
			new_clauses.remove(ci)

	return new_clauses

def implied(test, clause_list):
	for clause in clause_list:
		implied = True
		for t in test.term:
			if t not in clause.term:
				implied = False

		if implied:
			return True
	return False
