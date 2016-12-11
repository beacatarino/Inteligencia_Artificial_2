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

def find_unit_clause(clause_list, model, full_clause_list):

	new_assign = {}
	learned_from = []
	for clause in clause_list:

		# finds unit clause
		if len(clause.term) == 1:
			symb, val = get_symbol(clause.term[0])
			new_assign.update({symb: val})

			# gets clause that originated this
			for f_c in full_clause_list:
				if f_c.id == clause.id and clause.term[0] in f_c.term:
					orig_clause = deepcopy(f_c.term)
					# print(orig_clause)
					# print(clause.term[0])
					orig_clause.remove(clause.term[0])
					learned_from.append({clause.term[0]:orig_clause})
					# print("Learned from " + str(learned_from[-1]))

					return new_assign, learned_from

	return {},[]

def unit_propagation(node, unit_dict):

	node.model.update(unit_dict)

	# propagates the unit clause

	# removes clauses with the literal
	new_clauses = deepcopy(node.clauses)
	for symb, val in unit_dict.items():
		# print(symb)
		for clause in node.clauses:
			if get_literal(symb, val) in clause.term and clause.term in [c.term for c in new_clauses]:
				for c in new_clauses:
					if c.term == clause.term:
						new_clauses.remove(c)

	# print(new_clauses)
	node.clauses = new_clauses

	# print('After removing true clauses: \n' +  str(node.clauses))

	# removes clauses with negative of the literal
	for symb, val in unit_dict.items():
		for clause in node.clauses:
			neg_lit = neg(get_literal(symb, val))
			if neg_lit in clause.term:
				clause.term.remove(neg_lit)

	# print('After removing false clauses: \n' + str(node.clauses))

	return node

def checks_for_conflict(clause_list):

	for clause in clause_list:
		if clause.term == []:
			print("Conflict on term " + str(clause.id))
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
	for c in clauses:
		if c.term not in [clause.term for clause in unique_clauses]:
			unique_clauses.append(c)

	new_clauses = deepcopy(unique_clauses)

	for ci in unique_clauses:
		if not implied(ci, unique_clauses):
			# if at least on literal is not in a different clause, the
			#the two clauses dont imply each other
			new_clauses.remove(ci)


	return new_clauses

# Does all possible propagations and checks if the cnf reaches a conflict
def Deduce(node, clause_list):

	node.clauses = factorize_clauses(node.clauses)

	conflict_list = []
	unit_dict = None
	while unit_dict != {}:

		unit_dict, learned_from = find_unit_clause(node.clauses, unit_dict, clause_list)
		if learned_from != None:
			for le in learned_from:
				conflict_list.append(le)

		# for symb, val in unit_dict.items():
			# if symb in node.model:
				# if val != node.model[symb]:
					# return node,'CONFLICT', conflict_list

		node.model.update(unit_dict)
		node = unit_propagation(node, unit_dict)
		# print(node.clauses)

		conflict_exists, conflict_clause_id = checks_for_conflict(node.clauses)
		if conflict_exists:
			print('Check conflict at clause ' + str(conflict_clause_id))
			for c in clause_list:
				if c.id == conflict_clause_id:
					conflict_clause = deepcopy(c.term)
			print(conflict_clause)
			conflict_var = list(unit_dict.keys())[0]
			if len(conflict_clause) > 1:
				print(conflict_var)
				if unit_dict[conflict_var]:
					conflict_lit = neg(conflict_var)
					conflict_clause.remove(conflict_lit)
					conflict_list.append({conflict_lit : conflict_clause})
				else:
					conflict_clause.remove(conflict_var)
					conflict_list.append({conflict_var : conflict_clause})
			return node, 'CONFLICT', conflict_list, conflict_var

		if node.clauses == []:
			return node, 'SAT', [], None

	return node, 'UNSAT', conflict_list, None

def DecideNextBranch(node, level, backtrack, assign_list):

	# DLIS heuristic

	max_clauses = None
	for s in node.symbols:
		if not s in node.model:

			pos_lit = 0
			unsat_clauses = 0
			for c in node.clauses:
				if s in c.term or neg(s) in c.term:
					unsat_clauses = unsat_clauses + 1
					if s in c.term:
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

	# checks if already assigned as True
	assigned_true = False
	for assign in assign_list:
		if assign.value:
			if max_symbol == assign.id:
				assigned_true = True

	if not assigned_true and not backtrack and [max_symbol] not in node.clauses:
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
		for t in test.term:
			if t not in clause.term:
				implied = False

		if implied:
			return True
	return False

def AnalizeConflict(node, conflict_list, conflict_var, assign_list):

	if assign_list[-1].value == True:
		level = assign_list[-1].l
	else:
		level = assign_list[-1].l - 1

	min_conflict = None
	l_min = None

	# builds conflict graph
	pre_nodes = []
	implied_nodes = []
	for conflict in conflict_list:
		# nodes in conflict graph that imply other nodes
		pre_nodes.append(list(conflict.values())[0])
		# implied nodes, same index as the list of nodes that imply it in
		#pre_nodes
		implied_nodes.append(list(conflict.keys())[0])

	# print("Pre nodes : " + str(pre_nodes))
	# print("Implied Nodes : " + str(implied_nodes))

	# decision nodes that resulted in conflict
	decision_nodes = []
	for symb, val in node.model.items():
		decision_nodes.append(get_literal(symb, val))

	# print("Decision Nodes : " + str(decision_nodes))

	# finds reason for conflict node
	conflict_reasons = []
	for n_test in implied_nodes:
		if neg(n_test) in (implied_nodes + decision_nodes):
			conf_cl = [n_test, neg(n_test)]
			print("Found reason for conflict: " + str(conf_cl))
			conflict_reasons.append(conf_cl)

	if conflict_reasons == []:
		print("Something went wrong............")
		return None, level
	learnt_clause = []
	# builds conflict graph from conf_cl
	for conflict in conflict_list:
		if conf_cl[0] in conflict:
			learnt_clause += conflict[conf_cl[0]]
		if conf_cl[1] in conflict:
			learnt_clause += conflict[conf_cl[1]]

	# if this happens, search reason by the conflict_id
	# if conflict_reasons == []:
		# for c in clause_list:
			# print("Conflict\t\t\t" + str(conflict_id))
			# if c.id == conflict_id:
				# conf_cl = deepcopy(c.term)
				# for dec in decision_nodes:
					# if dec in conf_cl:
						# conf_cl.remove(dec)
				# print("Found reason for conflict: " + str(conf_cl))
				# conflict_reasons.append(conf_cl)


	print("Conflict list:" + str(conflict_list))

	# for conflict_dict in conflict_list:
		# conflict = list(conflict_dict.values())[0]
		# l = len(conflict)

		# # print(conflict)
		# neg_conflict = [neg(n) for n in conflict]
		# # print(neg_conflict)
		# # if conflict not in [c.term for c in node.clauses] and neg_conflict not in [c.term for c in node.clauses]:
		# if conflict != [] and conflict not in [c.term for c in node.clauses]:
			# if l_min == None:
				# min_conflict = conflict
				# l_min = l
			# elif l_min > l:
				# min_conflict = conflict
				# l_min = l

	

	print("Learned Clause: " + str(learnt_clause))
	return learnt_clause, level

def dpll(clauses, symbols):

	clause_list = []
	for c in clauses:
		if clause_list != []:
			id_clause = max([clause.id for clause in clause_list])+1
		else:
			id_clause = 0
		clause_list.append(Clause_term(id_clause, c))

	assign_list = []
	# node initialization
	node = Node(clause_list, symbols, {}, 0, None)
	#print("Initial clauses: " + str(clauses))
	backtrack = False

	level = 0

	while(True):
		level = level + 1
		node = DecideNextBranch(node, level, backtrack, assign_list)
		backtrack = False

		while(True):
			level = level + 1
			# print(node.model)
			node, status, conflict_list, conflict_var = Deduce(node, clause_list)
			# print(conflict_var)

			# for a in assign_list:
				# print ("Assignment " + a.id + ' ' + str(a.value) + ' ' + str(a.l))
			# print("Clauses: " + str(node.clauses))
			print("Status: " + str(status))
			for c in clause_list:
				print("Full Clauses, id:  " + str(c.id) + " clause: "+ str(c.term))

			#s = input('Continue?')
			if status == 'CONFLICT':
				learned_clause, level = AnalizeConflict(node, conflict_list, conflict_var, assign_list)

				# adds learned_clause
				n = node
				# while n != None and learned_clause != None:
				if learned_clause != None:
					if n.clauses != []:
						id_clause = max([clause.id for clause in n.clauses])+1
					else:
						id_clause = 0
					n.clauses.append(Clause_term(id_clause, learned_clause))
						# n = n.parent
					if clause_list != []:
						id_clause = max([clause.id for clause in clause_list])+1
					else:
						id_clause = 0
					clause_list.append(Clause_term(id_clause, learned_clause))

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
