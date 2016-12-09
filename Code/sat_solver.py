from mod_dpll_bea import dpll
# from mod_dpll import dpll


"""

#PSEUDO CODE DA P. 96 PARA DPLL CLOSE LEARNING - ITERACTIVE
#ALGORITMO 2.2

def sat_solver_algorithm(CNF_formula):
    b_level = 0

    while True:
        next_branch()
        while True:
            status = deduce_status()
            if status == conflict:
                analyse_conflict(b_level)
                if b_level == 0:
                    return False
                    Backtrack(b_level)
                elif status == SAT:
                    return (solution)
                else:
                    break
"""

def read_problem_line(line):

    line_list = line.split()

    variables = line_list[2]
    clauses = line_list[3]

    return variables, clauses

def read_cnf(cnf, verbose = 'False'):

    if verbose:
        print("Reading CNF file...")

    # variable initialization
    clause_list = []
    clause = []
    symbol_list = set([]) 

    read_clauses = False

    for line in cnf:

        # reads preamble

        # skips comment lines
        if line[0] == 'c':
            continue

        # reads problem line and then start reads clauses
        if line[0] == 'p':
            var_num, clau_num = read_problem_line(line)
            read_clauses = True
        elif read_clauses:
            literals = line.split()

            for lit in literals:

                # each clause is delimited by the '0' char
                if lit == '0':
                    clause_list.append(clause)

                    for l in clause:
                        if l[0] == '-':
                            l = l[1:]
                        symbol_list.add(l)

                    clause = []
                else:
                    clause.append(lit)

    if clause != []:
        clause_list.append(clause)
        
        for l in clause:
            if l[0] == '-':
                l = l[1:]
            symbol_list.add(l)
    
    if verbose:
        print("Done\n")
        print("Num of vars: " + var_num)
        print("Num of clauses: " + clau_num)
        print("CNF file has the following symbols:")
        for s in symbol_list:
            print("**** " + str(s) + " ****")
        print("CNF file has the following clauses:")
        for c in clause_list:
            print("** " + str(c) + " **")
        print('\n')
    return clause_list, symbol_list
    

def sat_solver(cnf, verbose = False):

    clauses, symbols = read_cnf(cnf, verbose = False)
   
    if verbose:
        print('Solving SAT...')

    sat,answer = dpll(clauses, symbols)

    if sat:        
        response = 'v '
        for (k,v) in answer.items():    
            if v == False:
                response += '-' + str(k) + ' '
            else:
                response += str(k) + ' '
        response += '0'
        print('Satisfiable')
        return response
    else:
        print('Not Satisfiable')

    return sat
