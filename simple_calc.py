def calc_commands(command_input):
    if command_input == "exit":
        return True
    elif command_input == "help":
        print('''The program calculates the algebraic sum of numbers, 
including variables''')
    else:
        print("Unknown command")
    return False

def assign_var(assignment_input, vars_dictionary):
    try:
        identifier, assignment = assignment_input.split('=')
    except ValueError:
        print("Invalid assignment")
    else:
        identifier = identifier.strip()
        assignment = assignment.strip()
        if not identifier.isalpha():
            print("Invalid identifier")
        elif assignment.isdigit():
            vars_dictionary[identifier] = assignment
        elif assignment.isalpha():
            try:
                vars_dictionary[identifier] = vars_dictionary[assignment]
            except KeyError:
                print("Unknown variable")
        else:
            print("Invalid assignment")

def simplify_summands(summands, vars_dictionary):
    simple_summands = []
    sign = 1
    for i, summand in enumerate(summands):
        if summand.isalpha():
            try:
                summand = vars_dictionary[summand]
            except KeyError:
                simple_summands = None
                break
        if summand.lstrip("+-").isdigit():
            try:
                simple_summands.append(sign * int(summand))
            except TypeError:
                print("Invalid expression")
            else:
                sign = 1
        elif i == len(summands) - 1:
            print("Invalid expression")
        elif summand.count("-"):
            sign *= (-1) ** summand.count("-")
    return simple_summands

dict_vars = {}
while True:
    user_input = input().strip()
    if len(user_input):
        if user_input.startswith('/'):
            exit_flag = calc_commands(user_input[1:])
            if exit_flag:
                break
        elif '=' in user_input:
            assign_var(user_input, dict_vars)
        elif user_input.isalpha():
            try:
                print(dict_vars[user_input])
            except KeyError:
                print("Unknown variable")
        else:
            try:
                print(sum(simplify_summands(user_input.split(), dict_vars)))
            except TypeError:
                print("Unknown variable")
print("Bye!")
