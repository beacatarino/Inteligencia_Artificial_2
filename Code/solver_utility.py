from copy import deepcopy

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

def implied(test, clause_list):
	for clause in clause_list:
		implied = True
		for t in test.term:
			if t not in clause.term:
				implied = False

		if implied:
			return True
	return False
