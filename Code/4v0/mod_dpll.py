from copy import deepcopy
from solver_utility import *

# Does all possible propagations and checks if the cnf reaches a conflict
def Deduce(node, clause_list):

	#node.clauses = factorize_clauses(node.clauses)

	conflict_list = []
	unit_dict = None
	while unit_dict != {}:

		unit_dict, learned_from = find_unit_clause(node)
		print(unit_dict)
		if learned_from != None:
			for le in learned_from:
				conflict_list.append(le)

		for symb, val in unit_dict.items():
			if symb in node.model:
				if val != node.model[symb]:
					return node,'CONFLICT', [], None

		node.model.update(unit_dict)
		node = unit_propagation(node, unit_dict)
		# print(node.clauses)

		conflict_exists, conflict_clause_id = checks_for_conflict(node.clauses)
		if conflict_exists:
		# 	print('Check conflict at clause ' + str(conflict_clause_id))
		# 	for c in clause_list:
		# 		if c.id == conflict_clause_id:
		# 			conflict_clause = deepcopy(c.term)
		# 	print(conflict_clause)
		# 	conflict_var = list(unit_dict.keys())[0]
		# 	if len(conflict_clause) > 1:
		# 		print(conflict_var)
		# 		if unit_dict[conflict_var]:
		# 			conflict_lit = neg(conflict_var)
		# 			conflict_clause.remove(conflict_lit)
		# 			conflict_list.append({conflict_lit : conflict_clause})
		# 		else:
		# 			conflict_clause.remove(conflict_var)
		# 			conflict_list.append({conflict_var : conflict_clause})
		 	return node, 'CONFLICT', [], None


		if check_sat(node.clauses):
			return node, 'SAT', [], None

	return node, 'UNSAT', conflict_list, None

def DecideNextBranch(node, level, backtrack, assign_list):

	# DLIS heuristic
	print(node.model)

	max_clauses = None
	for s in node.symbols:
		if not s in node.model:

			pos_lit = 0
			unsat_clauses = 0
			for c in node.clauses:
				if not c.res:
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
		decision = {max_symbol: True}
		print("Trying: " + str(max_symbol) + " as True at level " + str(level))
		assign_list.append( Assign_term(max_symbol, True, level) )
	else:
		decision = {max_symbol: False}
		print("Trying: " + str(max_symbol) + " as False at level " + str(level))

		# so the assignment can be repeated on a different iteration
		for a in assign_list:
			if a.id == max_symbol:
				assign_list.remove(a)
		# assign_list.remove(Assign_term(max_symbol,True,level))
		assign_list.append( Assign_term(max_symbol, False, level) )
	# new_model.append({max_symbol: True})True

	new_model.update(decision)

	#print("Current Mode: " + str(new_model))

	node = Node(deepcopy(node.clauses), node.symbols, new_model, level, node)
	node = unit_propagation(node, decision)

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

	print("Conflict list:" + str(conflict_list))


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
	node = Node(deepcopy(clause_list), symbols, {}, 0, None)
	#print("Initial clauses: " + str(clauses))
	backtrack = False

	level = 0

	while(True):
		level = level + 1
		node = DecideNextBranch(node, level, backtrack, assign_list)
		backtrack = False

		while(True):
			level = level + 1
			node, status, conflict_list, conflict_var = Deduce(node, clause_list)

			# for a in assign_list:
				# print ("Assignment " + a.id + ' ' + str(a.value) + ' ' + str(a.l))
			print("Status: " + str(status))
			print("Curr Model: " + str(node.model))
			for c in node.clauses:
				print("Full Clauses, id:  " + str(c.id) + " clause: "+ str(c.term) + " res: " + str(c.res) + " sat: " + str(c.sat) + " w: " + str(c.watched) + " index: " + str(c.nxt_lit) + " unit " + str(c.unit) + " unit_term " + str(c.unit_term))

			# s = input('Continue?')
			if status == 'CONFLICT':
				learned_clause, level = AnalizeConflict(node, conflict_list, conflict_var, assign_list)

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
					print("Current assignments: " + str(node.model))
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
