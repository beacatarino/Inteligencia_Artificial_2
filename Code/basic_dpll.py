from copy import deepcopy

# checks if all clauses are true
def all_clauses_true(clauses):

    for c in clauses:
        # if there isn't at least one true literal in the clause
        if True not in c:
            # clause isn't true
            return False

    return True

# checks if all clauses are true
def some_clauses_false(clauses):

    for c in clauses:
        not_false = False
        for l in c:

            # if there is at least one none false literal
            if l != False:
                not_false = True
        
        if not_false:
            continue

        # only when all literals are false 
        return True

    return False

def neg(literal):
    if literal == True:
        return False

    if literal == False:
        return True

    if literal[0] == '-':
        return literal[1:]
    else:
        return '-' + literal

def apply_model(clauses, model):

    model_clauses = []

    for c in clauses:

        clause = []

        for l in c:
            if l in model:
                model_l = model[l]
            elif neg(l) in model:
                model_l = not model[neg(l)]
            else:
                model_l = l
            
            clause.append(model_l)

        if True not in c:
            model_clauses.append(clause)

    return model_clauses

def check_sig(literal):
    if literal == True:
        return literal, True

    if literal == False:
        return literal, False

    if literal[0] == '-':
        # remove the '-'
        return literal[1:], False
    else:
        return literal, True

def get_unit_symbols(clauses):

    unit = {}

    for c in clauses:
        if len(c) == 1:
            l = c[0]    # unit symbol
            lit, val = check_sig(l)
            if lit not in [True, False]:
                unit[lit] = val

    return unit

def get_pure_symbols(clauses):

    pure = {}
    temp_pure = {}
    symbol_blacklist = [True, False]       # symbols that are not pure

    for c in clauses:
        for l in c:

            l, val = check_sig(l)

            if l not in temp_pure:
                temp_pure[l] = val
            elif temp_pure[l] != val:
                symbol_blacklist.append(l)

    # removes non pure symbols
    for p,v in temp_pure.items():
        if p not in symbol_blacklist:
            pure[p] = v

    return pure

def dpll(clauses, symbols, model):

    #print('Available symbols: ' + str(symbols))

    model_clauses = apply_model(clauses, model)
    #print('Current State:' + str(model_clauses))

    if all_clauses_true(model_clauses):
        return True

    if some_clauses_false(model_clauses):
        return False

    # if there are any pure symbols
    pure_symbols = get_pure_symbols(model_clauses)
    if len(pure_symbols) > 0:
        model_symbol = deepcopy(symbols)
        for p, v in pure_symbols.items():
            model[p] = v
            model_symbol.remove(p)
        return dpll(model_clauses, model_symbol, model)

    # if there are any unit symbols
    unit_symbols = get_unit_symbols(model_clauses)
    if len(unit_symbols) > 0:
        model_symbol = deepcopy(symbols)
        for u, v in unit_symbols.items():
            model[u] = v
            model_symbol.remove(u)
        return dpll(model_clauses, model_symbol, model)

    for s in symbols:
        rest = deepcopy(symbols)
        rest.remove(s)

        t_model = deepcopy(model)
        t_model.update({s:True})

        f_model = deepcopy(model)
        f_model.update({s:False})

        if dpll(model_clauses, rest, t_model) or dpll(model_clauses, rest, f_model):
            return True

    return False
