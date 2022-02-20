import functools
# Student: Boldisor Dragos-Alexandru
# Grupa: 332CB

# Clasa State generica
class State:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __lt__(self, other):
        return self.value < other.value

# Clasa Plus, reprezinta Regex-ul PLUS
class Plus:
    def __init__(self):
        self.value = None

    # folosit pentru debug
    def __str__(self):
        if self.value is None:
            return "Plus(?)"
        return "Plus(" + str(self.value) + ")"

    # folosit pentru a tine minte ca regex-ul PLUS are deja asignat un alt regex
    def add(self, other):
        self.value = other
        return True

    # transforma nfa-ul primit ca parametru aplicand algoritmul lui Thompson
    def transform(self, nfa, index):
        state_in = State(index)
        nfa.states.append(state_in)
        state_out1 = State(index + 1)
        nfa.states.append(state_out1)
        state_out2 = State(index + 2)
        nfa.states.append(state_out2)

        nfa.delta[(state_in, "epsilon")] = [nfa.q0]
        nfa.q0 = state_in
        nfa.delta[(nfa.final_states[0], "epsilon")] = [state_out1]
        nfa.final_states.pop()
        nfa.final_states.append(state_out2)

        nfa.delta[(state_out1, "epsilon")] = [state_out2, state_in]

# Asemanator Plus
class Star:
    def __init__(self):
        self.value = None

    def __str__(self):
        if self.value is None:
            return "Star(?)"
        return "Star(" + str(self.value) + ")"

    def add(self, other):
        self.value = other
        return True

    def transform(self, nfa, index):
        state_in1 = State(index)
        nfa.states.append(state_in1)
        state_in2 = State(index + 1)
        nfa.states.append(state_in2)
        state_out1 = State(index + 2)
        nfa.states.append(state_out1)
        state_out2 = State(index + 3)
        nfa.states.append(state_out2)

        nfa.delta[(state_in2, "epsilon")] = [nfa.q0]
        nfa.q0 = state_in1
        nfa.delta[(nfa.final_states[0], "epsilon")] = [state_out1]
        nfa.final_states.pop()
        nfa.final_states.append(state_out2)

        nfa.delta[(state_in1, "epsilon")] = [state_out2]
        nfa.delta[(state_out1, "epsilon")] = [state_in2]
        nfa.delta[(state_in1, "epsilon")].append(state_in2)
        nfa.delta[(state_out1, "epsilon")].append(state_out2)


# Asemanator Plus
class Union:
    def __init__(self):
        self.lvalue = None
        self.rvalue = None

    def __str__(self):
        string = "Union("
        if self.lvalue is None:
            string += "?,?)"
        else:
            string += (str(self.lvalue) + ",")
            if self.rvalue is None:
                string += "?)"
            else:
                string += (str(self.rvalue) + ")")
        return string

    def add(self, other):
        if self.lvalue is None:
            self.lvalue = other
            return False
        self.rvalue = other
        return True

    def transform(self, nfa1, nfa2, index):
        state_in = State(index)
        state_out = State(index + 1)
        nfa = Dfa()
        nfa.delta.update(nfa1.delta)
        nfa.delta.update(nfa2.delta)
        nfa.alphabet.extend(nfa1.alphabet)
        nfa.alphabet.extend(nfa2.alphabet)
        nfa.states.extend(nfa1.states)
        nfa.states.extend(nfa2.states)

        nfa.states.append(state_in)
        nfa.states.append(state_out)

        nfa.delta[(state_in, "epsilon")] = [nfa1.q0, nfa2.q0]
        nfa.q0 = state_in
        nfa.delta[nfa1.final_states[len(nfa1.final_states) - 1], "epsilon"] = [state_out]
        nfa.delta[nfa2.final_states[len(nfa2.final_states) - 1], "epsilon"] = [state_out]
        nfa.final_states.append(state_out)

        return nfa

# Asemanator Plus
class Concat:
    def __init__(self):
        self.lvalue = None
        self.rvalue = None

    def __str__(self):
        string = "Concat("
        if self.lvalue is None:
            string += "?,?)"
        else:
            string += (str(self.lvalue) + ",")
            if self.rvalue is None:
                string += "?)"
            else:
                string += (str(self.rvalue) + ")")
        return string

    def add(self, other):
        if self.lvalue is None:
            self.lvalue = other
            return False
        self.rvalue = other
        return True

    def transform(self, nfa1, nfa2):
        nfa = Dfa()
        nfa.delta.update(nfa1.delta)
        nfa.delta.update(nfa2.delta)
        nfa.alphabet.extend(nfa1.alphabet)
        nfa.alphabet.extend(nfa2.alphabet)
        nfa.states.extend(nfa1.states)
        nfa.states.extend(nfa2.states)

        nfa.q0 = nfa1.q0
        nfa.final_states.append(nfa2.final_states.pop())
        nfa.delta[(nfa1.final_states.pop(), "epsilon")] = [nfa2.q0]

        return nfa

# functie auxiliara folosita pentru a testa daca o stare se afla intr-o lista de stari
def contains(state, states):
    for x in states:
        if state.value == x.value:
            return True
    return False

# functie auxiliara folosita pentru a afisa un dictionar
def printDelta(delta):
    string = ""
    for key in delta.keys():
        string += (str(key[0]) + "," + str(key[1]) + " " + str([str(x) for x in delta[key]]) + "\n")
    return string

# Clasa Dfa, folosita pentru a reprezenta in memoria programului un DFA
class Dfa:

    def __init__(self):
        self.alphabet = []
        self.q0 = None
        self.states = []
        self.delta = {}
        self.final_states = []
        self.token_name = ""
        self.sink_state_verify = {}

    def __str__(self):
        string = ""
        for elem in self.alphabet:
            string += elem
        string += "\n" + str(len(self.states)) + "\n"
        string += str(self.q0) + "\n"
        for state in self.final_states:
            string += str(state) + " "
        string += "\n"
        for key in self.delta.keys():
            string += (str(key[0]) + ",'" + key[1] + "',")
            state_out = self.delta[key]
            string += str([str(x) for x in state_out]) + "\n"
        string = string[:-1]
        return string

    def next_conf(self, conf):
        if conf[1] == "":
            return contains(conf[0], self.final_states)
        state = conf[0]
        word = conf[1][1:]
        inp = conf[1][0]
        for trans in self.delta:
            if trans[0] == state and inp == trans[1]:
                return self.delta[trans], word
        return False

    def accepted(self, word):
        initial_conf = (self.q0, word)
        new_conf = self.next_conf(initial_conf)
        while new_conf is not False and new_conf is not True:
            new_conf = self.next_conf(new_conf)
        return new_conf

# Clasa ParseInfo -> functionalitatea se face prin metoda compute care
# primeste un fisier de specificatii. Aceasta returneaza o lista de nfa-uri.
# compute cheama pentru fiecare regex functia regex_to_nfa.
class ParseInfo:
    # Functie care primeste un index (numarul de la care vor fi numerotate
    # urmatoarele stari) si un string prin care se face tranzitia. Se foloseste
    # algoritmul lui Thompson.
    def compute_nfa(self, regex_string, index):
        nfa = Dfa()
        state_in = State(index)
        state_out = State(index + 1)
        nfa.q0 = state_in
        nfa.final_states.append(state_out)
        nfa.states.append(state_in)
        nfa.states.append(state_out)
        nfa.delta[(state_in, regex_string)] = [state_out]
        nfa.alphabet.append(regex_string)
        return nfa

    # Functie care primeste un string cu un regex si desparte in numele
    # acestuia de informatia utila
    def getTokenName(self, info):
        index = 0
        tokenName = ""
        while info[index] != ' ':
            tokenName += info[index]
            index += 1
        return tokenName, info[index:]

    # Functie care goleste stiva de operatori si aplica pe nfa-urile deja
    # existente
    def rest_of_stack(self, stack, nfa_stack, state_index):
        while len(stack) > 0:
            regex = stack.pop()
            if isinstance(regex, Plus):
                nfa = nfa_stack.pop()
                regex.transform(nfa, state_index)
                state_index += 3
                nfa_stack.append(nfa)
            elif isinstance(regex, Union):
                nfa1 = nfa_stack.pop()
                nfa2 = nfa_stack.pop()
                nfa_stack.append(regex.transform(nfa1, nfa2, state_index))
                state_index += 2
            elif isinstance(regex, Star):
                nfa = nfa_stack.pop()
                regex.transform(nfa, state_index)
                state_index += 4
                nfa_stack.append(nfa)
            else:
                nfa1 = nfa_stack.pop()
                nfa2 = nfa_stack.pop()
                nfa_stack.append(regex.transform(nfa2, nfa1))
        return nfa_stack.pop()

    # Functie care aplica toti operatorii din interioriul parantezei care
    # s-a inchis. Se apeleaza la intalnirea simbolului ')'
    def empty_parenthesis(self, stack, nfa_stack, state_index):
        regex = stack.pop()
        while regex != '(':
            if isinstance(regex, Plus):
                nfa = nfa_stack.pop()
                regex.transform(nfa, state_index)
                state_index += 3
                nfa_stack.append(nfa)
            elif isinstance(regex, Union):
                nfa2 = nfa_stack.pop()
                nfa1 = nfa_stack.pop()
                nfa_stack.append(regex.transform(nfa1, nfa2, state_index))
                state_index += 2
            elif isinstance(regex, Star):
                nfa = nfa_stack.pop()
                regex.transform(nfa, state_index)
                state_index += 4
                nfa_stack.append(nfa)
            else:
                nfa1 = nfa_stack.pop()
                nfa2 = nfa_stack.pop()
                nfa_stack.append(regex.transform(nfa2, nfa1))
            regex = stack.pop()
        return state_index

    # scoate din stiva de operatori toti operatorii care au prioritate mai
    # mare. (Este apelata cand se adauga in stiva de operatori Union sau Concat
    # si scoate Plus si Star pe care le aplica asupra nfa-urilor).
    def small_priority(self, stack, nfa_stack, state_index, new_regex):
        while len(stack) > 0:
            regex = stack.pop()
            if (not isinstance(regex, Plus)) and (not isinstance(regex, Star)):
                stack.append(regex)
                break
            nfa = nfa_stack.pop()
            if isinstance(regex, Plus):
                regex.transform(nfa, state_index)
                state_index += 3
            else:
                regex.transform(nfa, state_index)
                state_index += 4
            nfa_stack.append(nfa)
        stack.append(new_regex)
        return state_index

    # Functia apelata pentru fiecare regex. Citeste regexul si formeaza NFA-ul
    # care este returnat.
    def regex_to_nfa(self, info):
        stack = []
        nfa_stack = []
        tokenName, info = self.getTokenName(info)
        info = info.replace(";", "")
        info += ";"
        index = 0
        state_index = 0
        while index != len(info) and info[index] != ';':
            if info[index] == ' ':
                pass
            elif info[index] == '*':
                stack.append(Star())
                if info[index + 1] not in ")|+*;":
                    state_index = self.small_priority(stack, nfa_stack, state_index,
                                                      Concat())
            elif info[index] == '+':
                stack.append(Plus())
                if info[index + 1] not in ")|+*;":
                    state_index = self.small_priority(stack, nfa_stack, state_index,
                                                      Concat())
            elif info[index] == '|':
                state_index = self.small_priority(stack, nfa_stack, state_index, Union())
            elif info[index] == '(':
                stack.append(info[index])
            elif info[index] == ')':
                state_index = self.empty_parenthesis(stack, nfa_stack, state_index)
                if info[index + 1] not in ")|+*;":
                    state_index = self.small_priority(stack, nfa_stack, state_index,
                                                      Concat())
            elif info[index] == '\'':
                regex_string = ""
                index += 1
                while info[index] != '\'':
                    regex_string += info[index]
                    index += 1
                if regex_string == "\\n":
                    regex_string = "\n"
                nfa_stack.append(self.compute_nfa(regex_string, state_index))
                state_index += 2
                if info[index + 1] not in ")|+*;":
                    state_index = self.small_priority(stack, nfa_stack, state_index,
                                                      Concat())
            else:
                nfa_stack.append(self.compute_nfa(info[index], state_index))
                state_index += 2
                if info[index + 1] not in ")|+*;":
                    state_index = self.small_priority(stack, nfa_stack, state_index,
                                                      Concat())
            index += 1

        nfa = self.rest_of_stack(stack, nfa_stack, state_index)
        nfa.alphabet = list(dict.fromkeys(nfa.alphabet))
        nfa.token_name = tokenName
        return nfa

    def compute(self, info):
        all_info = info.split("\n")
        nfas = []
        for infoString in all_info:
            if (infoString != ""):
                nfas.append(self.regex_to_nfa(infoString))
        return nfas

# Clasa NfaToDfa -> prin functia compute primeste o lista de nfa-uri si aplica
# pentru fiecare transformarea de la nfa la dfa. La final, formeaza lexer-ul
# cu dfa-uri si il returneaza.
class NfaToDfa:
    def find_sink_state(self, dfa):
        for state in dfa.states:
            dfa.sink_state_verify[state] = False
        dfa.sink_state_verify[State(len(dfa.states) - 1)] = True

    # Functie care primeste un nfa si afla pentru fiecare stare epsilon
    # closure-ul
    def compute_epsilon_closure(self, nfa):
        epsilon_closure = {}
        for state in nfa.states:
            stack = [state]
            epsilon_closure[state] = []
            visited = [state]
            while len(stack) > 0:
                new_state = stack.pop()
                epsilon_closure[state].append(new_state)
                if (new_state, "epsilon") in nfa.delta.keys():
                    for element in nfa.delta[(new_state, "epsilon")]:
                        if element not in visited:
                            stack.append(element)
                            visited.append(element)
            epsilon_closure[state].sort()
        return epsilon_closure

    # Functie folosita la final pentru a copia restul de informatie din nfa in dfa
    # (ex: alfabetul) si pentru a face ultimele modificari necesare dfa-ului
    # (ex: aflarea starilor finale)
    def copy_nfa_to_dfa(self, dfa, nfa, decode_state, index):
        dfa.alphabet.extend(nfa.alphabet)
        dfa.token_name = nfa.token_name
        for state in dfa.states:
            for value in decode_state[state]:
                if value in nfa.final_states:
                    dfa.final_states.append(state)
                    break

        sink_state = State(index)
        dfa.states.append(sink_state)
        for key in dfa.delta.keys():
            if dfa.delta[key][0].value == "sink state":
                dfa.delta[key][0].value = index
        for elem in dfa.alphabet:
            dfa.delta[(sink_state, elem)] = [sink_state]

    # Functie de transformare din NFA in DFA
    def nfa_to_dfa(self, nfa):
        epsilon_closure = self.compute_epsilon_closure(nfa)
        decode_state = {}  # cheie: stare din DFA, valoare: lista de stari din NFA
        dfa = Dfa()

        index = 1
        state_q0 = State(0)
        sink_state = State("sink state")
        decode_state[sink_state] = []
        decode_state[state_q0] = epsilon_closure[nfa.q0]
        dfa.q0 = state_q0
        dfa.states.append(state_q0)
        queue = [state_q0]

        while len(queue) > 0:
            state_dfa = queue.pop(0)
            # Pentru fiecare stare aflam tranzitia cu fiecare element din alfabet
            for element in nfa.alphabet:
                destination = []
                for state in decode_state[state_dfa]:
                    if (state, element) in nfa.delta.keys():
                        destination.extend(epsilon_closure[nfa.delta[(state, element)][0]])
                # sortam ca sa comparam
                destination.sort()
                destination = list(set(destination))

                if destination not in decode_state.values():
                    # inseamna ca am gasit o stare noua in DFA
                    new_state = State(index)
                    index += 1
                    decode_state[new_state] = destination
                    dfa.states.append(new_state)
                    queue.append(new_state)
                    dfa.delta[(state_dfa, element)] = [new_state]
                else:
                    # cautam starea si adaugam tranzitia
                    for key in decode_state.keys():
                        if decode_state[key] == destination:
                            dfa.delta[(state_dfa, element)] = [key]
                            break

        self.copy_nfa_to_dfa(dfa, nfa, decode_state, index)
        self.find_sink_state(dfa)
        return dfa

    def compute(self, nfas):
        lexer = Lexer()
        for nfa in nfas:
            lexer.addDfa(self.nfa_to_dfa(nfa))
        return lexer

class Lexer:
    def __init__(self):
        self.dfas = [] # lista DFA-uri.
        self.states = [] # lista care retine starea in care se afla fiecare DFA.
        self.reject_states = [] # Lista care retine pentru fiecare DFA daca
        # a respins sau nu.
        self.lexems = [] # lista de lexeme.
        self.indices = [] # lista de indici pentru fiecare DFA.
        # Primul indice - de unde incepe lexemul. Al doilea - unde se termina.
        self.acceptance = False # True daca exista macar un DFA care a acceptat
        # un lexem.

    def addDfa(self, dfa):
        self.dfas.append(dfa)
        self.states.append(dfa.q0)
        self.reject_states.append(False)
        self.indices.append((0, -1))

    # Gaseste cel mai lung lexem. Daca toate automatele au respins, afiseaza
    # mesaj de eroare.
    def find_and_update(self, word, index):
        if self.acceptance is False:
            if index == -1:
                return "No viable alternative at character EOF, line 0"
            else:
                return "No viable alternative at character " + str(index) + ", line 0"
        longest_word = self.indices[0][1] - self.indices[0][0] + 1
        pos = 0
        # Aflam cel mai lung lexem.
        for i in range(1, len(self.dfas)):
            if longest_word < self.indices[i][1] - self.indices[i][0] + 1:
                longest_word = self.indices[i][1] - self.indices[i][0] + 1
                pos = i
        # Adaugam la lista de lexeme.
        self.lexems.append(str(self.dfas[pos].token_name) + " " + word[self.indices[pos][0]: self.indices[pos][1] + 1])
        # Returnam indicele la care am ajuns.
        return self.indices[pos][1] + 1

    def run(self, word):
        index = 0
        while index < len(word):
            for i in range(0, len(self.dfas)):
                if self.reject_states[i] is False:
                    # Pentru fiecare DFA, aplicam urmatorul input.
                    next_conf = self.dfas[i].next_conf((self.states[i], word[index] + " "))
                    # Daca nu exista tranzitie.
                    if next_conf is False:
                        self.reject_states[i] = True
                        continue
                    self.states[i] = next_conf[0][0]
                    # Daca tranzitia duce intr-un sink state.
                    if self.dfas[i].sink_state_verify[self.states[i]]:
                        self.reject_states[i] = True
                        continue
                    # Daca tranzitia duce intr-o stare finala.
                    if self.states[i] in self.dfas[i].final_states:
                        self.indices[i] = (self.indices[i][0], index)
                        self.acceptance = True
            # Daca toate au respins.
            if functools.reduce(lambda a, b: a & b, self.reject_states):
                last_position = self.find_and_update(word, index)
                # Daca este un mesaj de eroare.
                if isinstance(last_position, str):
                    return last_position
                for i in range(0, len(self.dfas)):  # se reseteaza DFA-urile.
                    self.reject_states[i] = False
                    self.indices[i] = (last_position, last_position - 1)
                    self.states[i] = self.dfas[i].q0
                index = last_position
                self.acceptance = False
            else:
                index += 1
        # La final, se mai face inca o cautare a ultimului posibil lexem.
        last_position = self.find_and_update(word, -1)
        if isinstance(last_position, str):
            return last_position
        res = ""
        for lexem in self.lexems:
            res += (lexem.replace("\n", "\\n") + "\n")
        return res

def runcompletelexer(lex_path, input_path, output_path):
    lex_file = open(lex_path, "r")
    parseInfo = ParseInfo()
    nfaToDfa = NfaToDfa()
    lexer = nfaToDfa.compute(parseInfo.compute(lex_file.read()))
    lex_file.close()

    input_file = open(input_path, "r")
    result = lexer.run(input_file.read())
    if result[len(result) - 1] == '\n':
        result = result[:-1]
    input_file.close()

    output_file = open(output_path, "w")
    output_file.write(result)
    output_file.close()
