from copy import deepcopy
from solver_utility import *

# Does all possible propagations and checks if the cnf reaches a conflict
def Deduce(node, clause_list):

	node.clauses = factorize_clauses(node.clauses)

	conflict_list = []
	unit_dict = None

	# while a new unit clause can be found
	while unit_dict != {}:

		unit_dict, learned_from = find_unit_clause(node.clauses, unit_dict, clause_list)
		if learned_from != None:
			for le in learned_from:
				conflict_list.append(le)

		# adds to model and propagates it
		node.model.update(unit_dict)
		node = unit_propagation(node, unit_dict)

		conflict_exists, conflict_clause_id = checks_for_conflict(node.clauses)
		if conflict_exists:

			# add possible conflict clause to a list
			for c in clause_list:
				if c.id == conflict_clause_id:
					conflict_clause = deepcopy(c.term)
			conflict_var = list(unit_dict.keys())[0]

			# removes current literal, this ways the assignment that originated
			#the conflict is isolated
			if len(conflict_clause) > 1:
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

	# DLIS heuristic - Dynamic Largest Individual Sum

	max_clauses = None
	for s in node.symbols:
		# checks all symbols not already in model
		if not s in node.model:

			pos_lit = 0
			unsat_clauses = 0
			for c in node.clauses:
				if s in c.term or neg(s) in c.term:
					unsat_clauses = unsat_clauses + 1
					if s in c.term:
						pos_lit += 1

			# finds the clause that appears in the most unsatisfied clauses
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

	# if the decision is being made because of a backtrack, try false
	if not assigned_true and not backtrack and [max_symbol] not in node.clauses:
		new_model.update({max_symbol: True})
		assign_list.append( Assign_term(max_symbol, True, level) )
	else:
		new_model.update({max_symbol: False})

		# so the assignment can be repeated on a different iteration
		for a in assign_list:
			if a.id == max_symbol:
				assign_list.remove(a)
		assign_list.append( Assign_term(max_symbol, False, level) )

	node = Node(node.clauses, node.symbols, new_model, level, node)
	node = unit_propagation(node, new_model)

	return node

def Backtrack(node, level, assign_list):

	if level == 0:
		return None, 0

	# backtracks to most recent true assignment, so a false assignment can be
	#attempted
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

	return node, level

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

	# decision nodes that resulted in conflict
	decision_nodes = []
	for symb, val in node.model.items():
		decision_nodes.append(get_literal(symb, val))

	# finds reason for conflict node
	conflict_reasons = []
	for n_test in implied_nodes:
		if neg(n_test) in (implied_nodes + decision_nodes):
			conf_cl = [n_test, neg(n_test)]
			conflict_reasons.append(conf_cl)

	if conflict_reasons == []:
		return None, level
	learnt_clause = []
	# builds conflict graph from conf_cl
	for conflict in conflict_list:
		if conf_cl[0] in conflict:
			learnt_clause += conflict[conf_cl[0]]
		if conf_cl[1] in conflict:
			learnt_clause += conflict[conf_cl[1]]

	return learnt_clause, level

def dpll(clauses, symbols):

	clause_list = init_clause_list(clauses)

	# node initialization
	node = Node(clause_list, symbols, {}, 0, None)

	backtrack = False
	level = 0
	assign_list = []

	while(True):
		level = level + 1
		node = DecideNextBranch(node, level, backtrack, assign_list)
		backtrack = False

		while(True):
			level = level + 1
			node, status, conflict_list, conflict_var = Deduce(node, clause_list)

			if status == 'CONFLICT':
				learned_clause, level = AnalizeConflict(node, conflict_list, conflict_var, assign_list)

				clause_list = add_learned_clause(node, clause_list, learned_clause)

				node, level = Backtrack(node, level, assign_list)

				if node == None:
					return False, {}

				backtrack = True
				break
			elif status == 'SAT':
				return True, node.model
			else:
				backtrack = False
				break
