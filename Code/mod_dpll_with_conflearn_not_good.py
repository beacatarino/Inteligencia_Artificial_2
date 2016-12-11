from copy import deepcopy

class Node:

	def __init__(self, clauses, symbols, model, level, parent):
		self.clauses = clauses
		self.symbols = symbols
		self.model = model          # after all unit propagations
		self.level = level
		self.parent = parent

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

def get_literal(symb, val):

	if val:
		return symb
	else:
		return '-' + symb

def neg(literal):

	if literal[0] == '-':
		return literal[1:]
	else:
		return '-' + literal

def find_unit_clause(clause_list, model):

	new_assign = {}
	for clause in clause_list:

		# finds unit clause
		if len(clause) == 1:
			symb, val = get_symbol(clause[0])
			new_assign.update({symb: val})

	return new_assign

def unit_propagation(node, unit_dict):

	node.model.update(unit_dict)

	# propagates the unit clause

	# removes clauses with the literal
	new_clauses = deepcopy(node.clauses)
	for symb, val in unit_dict.items():
		# print(symb)
		for clause in node.clauses:
			if get_literal(symb, val) in clause and clause in new_clauses:
				new_clauses.remove(clause)

	# print(new_clauses)
	node.clauses = new_clauses

	# print('After removing true clauses: \n' +  str(node.clauses))

	# removes clauses with negative of the literal
	for symb, val in unit_dict.items():
		for clause in node.clauses:
			neg_lit = neg(get_literal(symb, val))
			if neg_lit in clause:
				clause.remove(neg_lit)

	# print('After removing false clauses: \n' + str(node.clauses))

	return node

def checks_for_conflict(clause_list):

	for clause in clause_list:
		if clause == []:
			return True

	return False

def conflict_from_assignment(assign):

	conflict = []

	for symb, val in assign.items():
		conflict.append(get_literal(symb, not val))

	return conflict


def factorize_clauses(node):
	clauses = deepcopy(node.clauses)

	# removes duplicates
	unique_clauses = []
	for c in clauses:
		if c not in unique_clauses:
			unique_clauses.append(c)

	new_clauses = deepcopy(unique_clauses)

	for ci in unique_clauses:
		if not implied(ci, unique_clauses):
			# if at least on literal is not in a different clause, the
			#the two clauses dont imply each other
			new_clauses.remove(ci)

	node.clauses = new_clauses

	return node

# Does all possible propagations and checks if the cnf reaches a conflict
def Deduce(node):

	node = factorize_clauses(node)

	conflict_list = []
	unit_dict = None
	while unit_dict != {}:
		if unit_dict != None:	
			conflict_list.append(conflict_from_assignment(unit_dict))
		unit_dict = find_unit_clause(node.clauses, unit_dict)
		#print("Unit clause found: " + str(unit_dict))


		for symb, val in unit_dict.items():
			if symb in node.model:
				if val != node.model[symb]:
					print('model')
					return node,'CONFLICT', conflict_list

		node.model.update(unit_dict)
		node = unit_propagation(node, unit_dict)
		# print(node.clauses)

		if checks_for_conflict(node.clauses):
			print('Check conflict!')
			return node, 'CONFLICT', conflict_list

		if node.clauses == []:
			return node, 'SAT', []

	return node, 'UNSAT', conflict_list

def DecideNextBranch(node, level, backtrack, assign_list):

	# DLIS heuristic

	max_clauses = None
	for s in node.symbols:
		if not s in node.model:

			pos_lit = 0
			unsat_clauses = 0
			for c in node.clauses:
				if s in c or neg(s) in c:
					unsat_clauses = unsat_clauses + 1
					if s in c:
						pos_lit += 1

			if max_clauses == None:
				max_clauses = unsat_clauses
				max_symbol = s
				pos_lit_min = pos_lit
			elif unsat_clauses > max_clauses:
				max_clauses = unsat_clauses
				max_symbol = s
				pos_lit_min = pos_lit

	new_model = deepcopy(node.model)

	if not backtrack:
		new_model.update({max_symbol: True})
		print("Trying: " + str(max_symbol) + " as True at level " + str(level))
		assign_list.append( Assign_term(max_symbol, True, level) )
	else:
		new_model.update({max_symbol: False})
		print("Trying: " + str(max_symbol) + " as False at level " + str(level))

		# so the assignment can be repeated on a different iteration
		for a in assign_list:
			if a.id == max_symbol:
				assign_list.remove(a)
		# assign_list.remove(Assign_term(max_symbol,True,level))
		assign_list.append( Assign_term(max_symbol, False, level) )
	# new_model.append({max_symbol: True})True

	#print("Current Mode: " + str(new_model))

	node = Node(node.clauses, node.symbols, new_model, level, node)
	node = unit_propagation(node, new_model)

	return node

def Backtrack(node, level, assign_list):

	# curr_model = node.model
	# while node.model == curr_model:
	# # for x in range(blevel):
	#     node = node.parent
	#     level = level - 1
	#     print(node.decision_level)

	while (True):
		if not assign_list:
			level = 0
			node = node.parent
			break
		if assign_list[-1].value == False:
			node = node.parent
			assign_list.pop()
		else:
			node = node.parent
			level = assign_list[-1].l-1
			break

	#node.clauses.append(conflict)

	return node,level

def implied(test, clause_list):
	for clause in clause_list:
		implied = True
		for t in test:
			if t not in clause:
				implied = False

		if implied:
			return True
	return False

def AnalizeConflict(node, conflict_list, assign_list):

	min_conflict = None
	l_min = None

	for conflict in conflict_list:
		l = len(conflict)

		neg_conflict = [neg(n) for n in conflict]
		if conflict not in node.clauses and neg_conflict not in node.clauses:
			if l_min == None:
				min_conflict = conflict
				l_min = l
			elif l_min > l:
				min_conflict = conflict
				l_min = l

	if assign_list[-1].value == True:
		level = assign_list[-1].l
	else:
		level = assign_list[-1].l - 1

	print("Learned Clause: " + str(min_conflict))
	return min_conflict, level

def dpll(clauses, symbols):

	assign_list = []
	# node initialization
	node = Node(clauses, symbols, {}, 0, None)
	#print("Initial clauses: " + str(clauses))
	backtrack = False

	level = 0

	while(True):
		level = level + 1
		node = DecideNextBranch(node, level, backtrack, assign_list)
		backtrack = False

		while(True):
			level = level + 1
			node, status, conflict_list = Deduce(node)

			# for a in assign_list:
				# print ("Assignment " + a.id + ' ' + str(a.value) + ' ' + str(a.l))
			print("Clauses: " + str(node.clauses))
			print("Status: " + str(status))

			#s = input('Continue?')
			if status == 'CONFLICT':
				learned_clause, level = AnalizeConflict(node, conflict_list, assign_list)

				# adds learned_clause
				n = node
				while n != None and learned_clause != None:
					n.clauses.append(learned_clause)
					n = n.parent

				if level == 0:
					return False, {}
				print("Level before backtrack: " + str(level))
				print("BACKTRACKING")
				node, level = Backtrack(node, level, assign_list)
				# if level == 0:
				#     return False, {}
				# node= Backtrack(node, conflict, level)
				if node != None:
					print("Current level: " + str(level))
					# print("Current assignments: " + str(node.model))
				else:
					print("Current level: " + str(level))
					return False, {}
				backtrack = True
				break
			elif status == 'SAT':
				return True, node.model
			else:
				backtrack = False
				# level = 0
				# assign_list = []
				break
