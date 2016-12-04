from copy import deepcopy


class Node:
    
    def __init__(self, c, s, m, dm, p, l,bl):
        self.clauses = c
        self.symbols = s
        self.model = m
        self.decision_model = dm     # only updated when we decide a new branch
        self.parent = p
        self.level = l
        self.blevel = bl

def get_value(symbol):

    if symbol[0] == '-':
        return False
    else:
        return True

def neg(symbol):

    if symbol[0] == '-':
        return symbol[1:]
    else:
        return '-' + symbol

def get_symb(literal):

    if literal[0] == '-':
        return literal[1:]
    else:
        return literal

def unit_propagation(node):

    clauses = node.clauses
    model = node.model

    new_assigns = {}
    used_models = []


    new_clauses = deepcopy(clauses)
    for symb, assig in model.items():
        for c in clauses:

            # when the literal is True
            if (assig and symb in c) or (not assig and neg(symb) in c):

                # only keep unsatified clauses
                if c in new_clauses:
                    new_clauses.remove(c)
    

        for c in clauses:
            # when the literal is False
            if (not assig and symb in c) or (assig and neg(symb) in c):
                # updates the clause, removing the False literal
                new_c = deepcopy(c)
                if symb in new_c:
                    new_c.remove(symb)
                else:
                    new_c.remove(neg(symb))

                if new_c not in new_clauses and c in new_clauses:
                    new_clauses.append(new_c)
                    new_clauses.remove(c)
                # print("Removed literal in a clause " + str(new_c))
                

        for new_c in new_clauses:
            # new assignment learned from the generation of a unit clause
            if len(new_c) == 1:
                # print("NEW ASSIGNMENT")
                new_assigns[get_symb(new_c[0])] = get_value(new_c[0])
                used_models.append({symb: assig})

    new_model = deepcopy(model)
    new_model.update(new_assigns)


    return(new_clauses, new_model, used_models)

# Using DLIS heuristic
def DecideNextBranch(node, backtrack):

    max_unsat_clauses = None


    # finds symbols in most unsatisfied clauses
    for s in node.symbols:

        unsat_clauses = 0
        for c in node.clauses:
            if s in c or neg(s) in c:
                unsat_clauses = unsat_clauses + 1

        if max_unsat_clauses == None:
            max_unsat_clauses = unsat_clauses
            decision_symbol = s
        elif unsat_clauses > max_unsat_clauses: 
            max_unsat_clauses = unsat_clauses
            decision_symbol = s

    clauses = deepcopy(node.clauses)
    symbols = deepcopy(node.symbols)
    #symbols.remove(decision_symbol)
    model = deepcopy(node.model)

    # first tries assigning true. If this leads to a backtrack, try false
    if backtrack:
        model[decision_symbol] = False
    else:
        model[decision_symbol] = True

    node.clauses = clauses
    node.symbols = symbols
    node.model = model
    node.decision_model = model

    return node

def check_UIP(branch_model, used_model):

    for bm in branch_model:
        if bm in used_model:
            return False

    return True

def get_clause_from_used_models(model):

    clause = []
    for symb, val in model.items():
        if val:
            clause.append(neg(symb))
        else:
            clause.append(symb)

    return(clause)


def get_conflict_clause(node, used_model):

    if check_UIP(node.decision_model, used_model):
        return get_clause_from_used_models(node.model)

def get_status(node, used_model):

    if len(node.clauses) == 0:
        print('\nSolution')
        print(node.model)
        return 'SAT'

    for c in node.clauses:
        if len(c) == 0:
            return 'CONFLICT'

    if used_model == []:
        return 'UNSAT'

    return 'CONTINUE'

def DecideStatus(node, level, blevel):

    new_clauses, new_model, used_model = unit_propagation(node)

    # creates new node
    node = Node(new_clauses, node.symbols, new_model, node.decision_model, node, level, blevel)

    # possible conflict clause
    conflict_clause = get_conflict_clause(node, used_model)

    status = get_status(node, used_model)

    return status, node, conflict_clause


def Backtrack(node, blevel, conflict_clause):

    #for level_count in range(blevel):

    while node.level != blevel:
        node = node.parent

    if node != None:
        if conflict_clause not in node.clauses:
            node.clauses.append(conflict_clause)

    return node

def dpll(clauses, symbols, model):

    backtrack = False       # indicates if a backtrack is performed

    # initial node
    init = Node(clauses, symbols, model, [], None, 0, 0 )
    node = deepcopy(init)
    node.level = 1
    node.parent = init

    level = 1
    blevel = 1
    while True:

        node = DecideNextBranch(node, backtrack)
        print("Try model: " + str(node.model))

        if backtrack:
            level = node.blevel
            if node.parent != None:
                blevel = node.parent.blevel
            backtrack = False
        else:
            blevel = level

        while True:
            level = level + 1
            status, node, conflict_clause = DecideStatus(node, level, blevel)
            print("\nNew node:")
            node.blevel = blevel
            print("Clauses: " + str(node.clauses))
            print("Status: " + status)
            if status == "CONFLICT":
                backtrack = True
                print("BACKTRACKING " + str(level - node.blevel) + " level(s)")
                print("Current: " + str(node.level))
                print("Target: " + str(blevel))
                node = Backtrack(node, blevel, conflict_clause)

                print("Current: " + str(node.level))
                print("Current: " + str(node.blevel))
                if node.parent == None:
                    return False
                break

            if status == "SAT":
                return True
            elif status == "UNSAT":
                break

    return False
