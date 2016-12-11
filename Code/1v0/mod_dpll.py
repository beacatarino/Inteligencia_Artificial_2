import random
from solver_utility import *

class Node:

	# will indicate the current status of the assginment
	def __init__(self, clauses, decision, implied, level, parent):
		self.clauses = clauses 			# current clauses
		self.decision = decision		# all decision assignments
		self.implied = implied 		 	# all assignments implied from decision
		self.level = level 				# depth of the current node
		self.parent = parent 			# pointer to previous node

class Problem:

	# class stating problem conditions (not mutable)
	def __init__(self, clauses, symbols):
		self.clauses = clauses 			# initial clauses
		self.symbols = symbols 			# symbols

# Does all possible propagations and checks if the cnf reaches a conflict
def Deduce(node):


	model = deepcopy(node.decision)
	for assign in node.implied:
		model.update(assign)

	node = unit_propagation(node, model)

	# assignments from unit clauses
	unit_dict = None
	while unit_dict != {}:

		unit_dict = find_unit_clause(node.clauses, model)
		# print("Unit clause(s) found: " + str(unit_dict))


		# if the assignment give a contradiction
		for symb, val in unit_dict.items():
			if symb in model:
				if val != model[symb]:
					return node,'CONFLICT'

		node.implied.append(unit_dict)
		model.update(unit_dict)

		node = unit_propagation(node, unit_dict)

	# print(node.clauses)

	if checks_for_conflict(node.clauses):
		return node, 'CONFLICT'

	if node.clauses == []:
		return node, 'SAT'

	return node, 'UNSAT'

def DecideNextBranch(node, problem, level, explored_decisions):

	# DLIS heuristic

	# max_clauses = None
	# for s in node.symbols:
		# if not s in node.model:

			# pos_lit = 0
			# unsat_clauses = 0
			# for c in node.clauses:
				# if s in c:
					# if s not in assign_blacklist:
						# unsat_clauses = unsat_clauses + 1
						# pos_lit += 1
					# else:
						# if not assign_blacklist[s]:
							# unsat_clauses = unsat_clauses + 1
							# pos_lit += 1

				# if neg(s) in c:
					# if s not in assign_blacklist:
						# unsat_clauses = unsat_clauses + 1
						# pos_lit += 1
					# else:
						# if assign_blacklist[s]:
							# unsat_clauses = unsat_clauses + 1
							# pos_lit += 1

		# if max_clauses == None:
			# max_clauses = unsat_clauses
			# max_symbol = s
			# pos_lit_min = pos_lit
		# elif unsat_clauses > max_clauses:
			# max_clauses = unsat_clauses
			# max_symbol = s
			# pos_lit_min = pos_lit

	# new_model = deepcopy(node.model)

	# if pos_lit > max_clauses/2:
		# new_model.update({max_symbol: True})
		# assign_blacklist.update({max_symbol: True})
		# print("Trying: " + str(max_symbol) + " as True")
	# else:
		# new_model.update({max_symbol: False})
		# assign_blacklist.update({max_symbol: False})
		# print("Trying: " + str(max_symbol) + " as False")
		# # new_model.update({max_symbol: bool(random.getrandbits(1))})

	# Random
	new_decision = {}
	found_decision = False
	for symb in problem.symbols:
		for val in [True, False]:
			new_decision = deepcopy(node.decision)
			new_decision.update({symb: val})
			if new_decision not in explored_decisions:
				found_decision = True
				break
		if found_decision:
			break

	if found_decision == False:
		node, level = Backtrack(node, level)
		# node, level = Backtrack(node, level)
		return  DecideNextBranch(node, problem, level, explored_decisions)

	# while new_decision in explored_decisions:
		# new_decision = deepcopy(node.decision)
		# decision_symb = random.sample(problem.symbols, 1)[0]
		# if decision_symb not in new_decision:
			# new_decision.update({decision_symb: bool(random.getrandbits(1))})
	# print(new_decision)

	explored_decisions.append(new_decision)
	print("Current Decision: " + str(new_decision))

	node = Node(problem.clauses, new_decision, node.implied, level, node)
	# node = unit_propagation(node, new_decision)

	return node, explored_decisions

def Backtrack(node, level):

	bad_decision = node.decision

	# for x in range(num_backtracks):
	# while blevel != level:
	while node.decision == bad_decision:
		node = node.parent
		level -= 1

	node.implied = []

	return node, level

def AnalyzeConflict(node, problem, conflict_list):

	if node.parent == None:
		return None

	l_min = None
	min_conflict = []
	for conflict in conflict_list:
		l = len(conflict)

		if conflict not in problem.clauses and not isimplied(conflict, problem.clauses):
			# print(conflict)
			# print(node.clauses)
			if l_min == None:
				min_conflict = conflict
				l_min = l
			elif l_min > l:
				min_conflict = conflict
				l_min = l

	if min_conflict == []:
		# node = node.pa#rent
		print("Nothing has been learnt")
		return None

	print("Learned Clause: " + str(min_conflict))
	return min_conflict

def dpll(clauses, symbols):

	print("Initial clauses: " + str(clauses))	

	# node initialization
	node = Node(clauses, {}, [], 0, None)
	problem = Problem(clauses, symbols)

	level = 0

	# so no decisions are repeated
	explored_decisions = [{}]

	while(True):
		node, explored_decisions = DecideNextBranch(node, problem, level, explored_decisions)
		if node == None:
			print("Reason: Lack of assignments to perform")
			return False, {}

		# print(explored_decisions)
		node = factorize_clauses(node, problem)
		level = level + 1
		print("Clauses from decision " + str(node.clauses))

		while(True):
			node, status = Deduce(node)
			print("Current Clauses " + str(node.clauses))

			# s = input('Continue?')
			if status == 'CONFLICT':
				conflict = AnalyzeConflict(node, problem, node.implied)
				print(conflict)
				problem.clauses.append(conflict_from_assignment(conflict))
				print("BACKTRACKING")
				print("From level: " + str(node.level))
				node, level = Backtrack(node, level)
				if node == None or node.level <= 0:
					print("Reached initial node")
					return False, {}
				print("To level: " + str(node.level))
				print("Back to Decision: " + str(node.decision))
				break
			elif status == 'SAT':
				model = deepcopy(node.decision)
				for imp in node.implied:
					model.update(imp)
				return True, model
			else:
				break
