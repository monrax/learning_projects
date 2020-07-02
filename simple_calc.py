class SmartCalc:
    def __init__(self):
        self.variables = {}
        self.postfix_stack = []
        self.exit_flag = False

    def exec_command(self, command_input):
        if command_input == "/exit":
            self.exit_flag = True
        elif command_input == "/help":
            print('''The program calculates the algebraic sum of numbers, 
                    including variables''')
        else:
            print("Unknown command")

    def store_variable(self, assignment_input):
        if assignment_input.count('=') == 1:
            identifier, assignment = assignment_input.split('=')
            identifier = identifier.strip()
            assignment = assignment.strip()
            if not identifier.isalpha():
                print("Invalid identifier")
            elif assignment.isdigit():
                self.variables[identifier] = assignment
            elif assignment.isalpha():
                if assignment in self.variables:
                    self.variables[identifier] = self.variables[assignment]
                else:
                    print("Unknown variable")
            else:
                print("Invalid assignment")
        else:
            print("Invalid assignment")

    def postfix_stack2ans(self):
        ans = []
        for i in self.postfix_stack:
            if i.isdigit():
                ans.append(int(i))
            else:
                a = ans.pop()
                b = ans.pop()
                if i == '+':
                    ans.append(b + a)
                elif i == '-':
                    ans.append(b - a)
                elif i == '*':
                    ans.append(b * a)
                elif i == '/':
                    ans.append(b / a)
                elif i == '^':
                    ans.append(b ** a)
        self.postfix_stack.clear()
        return ans[0]

    def infix2postfix_stack(self, expression):
        precedence = {'+': 0, '-': 0, '*': 1, '/': 1, '^': 2}
        operators = []
        for i in expression:
            if i.isdigit():
                self.postfix_stack.append(i)
            elif not operators or '(' in (operators[-1], i):
                operators.append(i)
            elif i == ')':
                while operators[-1] != '(':
                    self.postfix_stack.append(operators.pop())
                operators.pop()
            else:
                while precedence[i] <= precedence[operators[-1]]:
                    self.postfix_stack.append(operators.pop())
                    if not operators or operators[-1] == '(':
                        break
                operators.append(i)
        while operators:
            self.postfix_stack.append(operators.pop())

    def parse_input(self, input_expression):
        parsed_input = []
        if input_expression.count('(') != input_expression.count(')'):
            print("Invalid expression")
            return parsed_input

        input_expression = input_expression.split()
        for i in range(len(input_expression) - 1):
            if (input_expression[i].strip("()").isalnum() and
                    input_expression[i + 1].strip("()").isalnum()):
                print("Invalid expression")
                return parsed_input

        input_expression = "".join(input_expression)
        for i in input_expression:
            if parsed_input:
                if i.isdigit():
                    if parsed_input[-1].isdigit():
                        parsed_input.append("".join([parsed_input.pop(), i]))
                    else:
                        parsed_input.append(i)
                elif i.isalpha():
                    if parsed_input[-1].isalpha():
                        parsed_input.append("".join([parsed_input.pop(), i]))
                    else:
                        parsed_input.append(i)
                elif i in ('(', ')'):
                    parsed_input.append(i)
                else:
                    if parsed_input[-1].isalnum() or parsed_input[-1] in ('(', ')'):
                        parsed_input.append(i)
                    else:
                        parsed_input.append("".join([parsed_input.pop(), i]))
            else:
                parsed_input.append(i)

        for i, chunk in enumerate(parsed_input):
            if chunk.isalpha():
                if chunk in self.variables:
                    parsed_input[i] = self.variables[chunk]
                else:
                    parsed_input.clear()
                    # print(f"Unknown variable: {chunk}")
                    print("Unknown variable")
                    break
            elif not chunk.isdigit() and len(chunk) > 1:
                if '*' in chunk or '/' in chunk or '^' in chunk:
                    parsed_input.clear()
                    print("Invalid expression")
                    break
                elif '-' in chunk:
                    parsed_input[i] = '-' if chunk.count('-') % 2 else "+"
                elif '+' in chunk:
                    parsed_input[i] = '+'

        return parsed_input

    def run(self):
        while not self.exit_flag:
            user_input = input().strip()
            if len(user_input):
                if user_input.startswith('/'):
                    self.exec_command(user_input)
                elif '=' in user_input:
                    self.store_variable(user_input)
                else:
                    user_input = self.parse_input(user_input)
                    if user_input:
                        self.infix2postfix_stack(user_input)
                        print(self.postfix_stack2ans())
        print("Bye!")


new_calc = SmartCalc()
new_calc.run()
