from copy import deepcopy

class Node:
    
    def __init__(self, clauses, symbols, model, level, parent):
        self.clauses = clauses
        self.symbols = symbols
        self.model = model          # after all unit propagations
        self.level = level
        self.parent = parent

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
        unit_dict = find_unit_clause(node.clauses, node.model)
        print("Unit clause found: " + str(unit_dict))

        conflict_list.append(conflict_from_assignment(unit_dict))

        for symb, val in unit_dict.items():
            if symb in node.model:
                if val != node.model[symb]:
                    return node,'CONFLICT', conflict_list

        node.model.update(unit_dict)
        node = unit_propagation(node, unit_dict)
        # print(node.clauses)

        if checks_for_conflict(node.clauses):
            return node, 'CONFLICT', conflict_list

        if node.clauses == []:
            return node, 'SAT', []

    return node, 'UNSAT', conflict_list

def DecideNextBranch(node, level, backtrack):

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
        print("Trying: " + str(max_symbol) + " as True")
    else:
        new_model.update({max_symbol: False})
        print("Trying: " + str(max_symbol) + " as False")
    # new_model.append({max_symbol: True})

    print("Current Mode: " + str(new_model))

    node = Node(node.clauses, node.symbols, new_model, level, node)
    node = unit_propagation(node, new_model) 

    return node

def Backtrack(node, conflict, level):

    curr_model = node.model
    while node.model == curr_model:
    # for x in range(blevel):
        node = node.parent
        level = level - 1
        # print(node.decision_level)

    node.clauses.append(conflict)
    return node

def implied(test, clause_list):
    for clause in clause_list:
        implied = True
        for t in test:
            if t not in clause:
                implied = False
                
        if implied:
            return True
    return False

def AnalizeConflict(node, conflict_list):

    l_min = None
    for conflict in conflict_list:
        l = len(conflict)

        if conflict not in node.clauses and not implied(conflict, node.clauses):
            if l_min == None:
                min_conflict = conflict
                l_min = l
            elif l_min > l:
                min_conflict = conflict
                l_min = l

    print("Learned Clause: " + str(min_conflict))
    return min_conflict

def dpll(clauses, symbols):

    # node initialization
    node = Node(clauses, symbols, {}, 0, None)
    print("Initial clauses: " + str(clauses))
    level = 0
    backtrack = False

    while(True):
        level = level + 1
        node = DecideNextBranch(node, level, backtrack)
        backtrack = False

        while(True):
            level = level + 1
            node, status, conflict_list= Deduce(node)
            print(node.clauses)
            print(status)

            s = input('Continue?')
            if status == 'CONFLICT':
                conflict = AnalizeConflict(node, conflict_list)
                print("BACKTRACKING")
                node= Backtrack(node, conflict, level)
                print("Current level: " + str(node.level))
                print("Current assignments: " + str(node.model))
                backtrack = True
                if node.level == None:
                    return False, {}
                # break
            elif status == 'SAT':
                return True, node.model
            else:
                break

        
