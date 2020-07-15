class Mat:
    def __init__(self, n_rows, m_columns, matrix=None):
        self.rows = n_rows
        self.cols = m_columns
        self.dim = (self.rows, self.cols)
        self.matrix = matrix[:] if matrix else []

    def __add__(self, other):
        if self.dim == other.dim:
            res = Mat(*self.dim)
            for i in range(self.rows):
                res.matrix.append([
                    self.matrix[i][j] + other.matrix[i][j]
                    for j in range(self.cols)
                ])
            return res
        else:
            return "The operation cannot be performed."

    def __mul__(self, const):
        res = Mat(*self.dim)
        for i in self.matrix:
            res.matrix.append([const * j for j in i])
        return res

    def __rmul__(self, const):
        return self.__mul__(const)

    def __matmul__(self, other):
        if self.cols == other.rows:
            res = Mat(self.rows, other.cols)
            for i in self.matrix:
                res.matrix.append([
                    sum([ei * ej for ei, ej in zip(i, j)])
                    for j in other.transpose().matrix
                ])
            return res
        else:
            return "The operation cannot be performed."

    def __str__(self):
        res = ''
        for i in self.matrix:
            res += ' '.join(map(str, i))
            res += '\n'
        return res[:-1]

    def __repr__(self):
        return "{}\n{}".format(object.__repr__(self), str(self))

    def transpose(self):
        res = Mat(self.cols, self.rows)
        for j in range(self.cols):
            res.matrix.append([i[j] for i in self.matrix])
        return res

    def side_transpose(self):
        res = Mat(self.cols, self.rows)
        for j in reversed(range(self.cols)):
            res.matrix.append([i[j] for i in self.matrix[::-1]])
        return res

    def v_transpose(self):
        res = Mat(*self.dim)
        for i in self.matrix:
            res.matrix.append(i[::-1])
        return res

    def h_transpose(self):
        res = Mat(*self.dim)
        res.matrix = self.matrix[::-1]
        return res

    def input_matrix(self):
        self.matrix = [[float(j) for j in input().split()]
                       for _i in range(self.rows)]

    def append_rows(self, rows):
        self.rows += rows
        for i in range(rows):
            self.matrix.append([float(j) for j in input().split()])

    def print(self):
        for i in self.matrix:
            print(*i)

    def cof(self, row_index):
        if self.rows == self.cols:
            excluded_row = Mat(1, self.cols, [self.matrix[row_index]])
            cofactors = Mat(1, self.cols, [[]])
            for col in range(excluded_row.cols):
                minor = Mat(self.rows - 1, self.cols - 1)
                minor.matrix = [
                    [row[j] for j in range(excluded_row.cols) if j != col]
                    for i, row in enumerate(self.matrix) if i != row_index
                ]
                cofactors.matrix[0].append((-1) ** (row_index + col) * minor.det())
            return cofactors
        else:
            return "The operation cannot be performed."

    def det(self):
        if self.rows == self.cols:
            if self.rows == 1:
                return self.matrix[0][0]
            if self.rows == 2:
                return (self.matrix[0][0] * self.matrix[1][1]) - (
                        self.matrix[0][1] * self.matrix[1][0])
            else:
                row_0 = Mat(1, self.cols, [self.matrix[0]])
                return (row_0 @ self.cof(0).transpose()).matrix[0][0]
        else:
            return "The operation cannot be performed."

    def adj(self):
        if self.rows == self.cols:
            cof_matrix = Mat(*self.dim)
            for i in range(self.rows):
                cof_matrix.matrix.append(self.cof(i).matrix[0])
            return cof_matrix.transpose()
        else:
            return "The operation cannot be performed."

    def inv(self):
        det = self.det()
        if isinstance(det, str):
            return "This matrix doesn't have an inverse."
        elif det != 0:
            return (1 / det) * self.adj()


while True:
    choice = input('''1. Add matrices
                      2. Multiply matrix by a constant
                      3. Multiply matrices
                      4. Transpose matrix
                      5. Calculate a determinant
                      6. Inverse matrix
                      0. Exit
                      Your choice: '''.replace("  ", ''))
    if len(choice):
        if choice == '0':
            break
        elif choice in ('1', '3'):
            n, m = (int(i) for i in input(
                "Enter size of first matrix: ").split())
            a = Mat(n, m)
            print("Enter first matrix:")
            a.input_matrix()
            n, m = (int(i) for i in input(
                "Enter size of second matrix: ").split())
            b = Mat(n, m)
            print("Enter second matrix:")
            b.input_matrix()
            print("The result is:")
            print(a + b if choice == '1' else a @ b, end='\n' * 2)
        elif choice == '2':
            n, m = (int(i) for i in input(
                "Enter size of matrix: ").split())
            a = Mat(n, m)
            print("Enter matrix:")
            a.input_matrix()
            c = float(input("Enter constant: "))
            print("The result is:")
            print(c * a, end='\n' * 2)
        elif choice == '4':
            transpose_choice = input('''
            1. Main diagonal
            2. Side diagonal
            3. Vertical line
            4. Horizontal line
            Your choice: ''')
            n, m = (int(i) for i in input(
                "Enter matrix size: ").split())
            a = Mat(n, m)
            print("Enter matrix:")
            a.input_matrix()
            print("The result is:")
            if transpose_choice == '1':
                transpose = a.transpose()
            elif transpose_choice == '2':
                transpose = a.side_transpose()
            elif transpose_choice == '3':
                transpose = a.v_transpose()
            elif transpose_choice == '4':
                transpose = a.h_transpose()
            else:
                transpose = a
            print(transpose, end='\n' * 2)
        elif choice in ('5', '6'):
            n, m = (int(i) for i in input(
                "Enter matrix size: ").split())
            a = Mat(n, m)
            print("Enter matrix:")
            a.input_matrix()
            if choice == '5':
                determinant = a.det()
                if isinstance(determinant, str):
                    print(f"{determinant}\n")
                else:
                    print(f"The result is:\n{determinant}\n")
            else:
                inverse = a.inv()
                if isinstance(inverse, str):
                    print(f"{inverse}\n")
                else:
                    print(f"The result is:\n{inverse}\n")
