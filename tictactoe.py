import random


def into_rows(cells, n=3):
    return [cells[i * n: (i + 1) * n] for i in range(n)]


def into_cols(cells, m=3):
    matrix = into_rows(cells)
    transpose = [[row[j] for row in matrix] for j in range(m)]
    return transpose


def add_borders(matrix_rows):
    lid = ['-' * (len(matrix_rows[0]) * 2 + 3)]
    side = ['|']
    bordered_rows = [lid]
    for row in matrix_rows:
        bordered_rows.append(side + row + side)
    bordered_rows.append(lid)
    return bordered_rows


def print_field(cells):
    rows = into_rows(cells)
    matrix_field = add_borders(rows)
    for i in matrix_field:
        print(*i)


def is_unfinished(cells):
    return ' ' in cells


def is_impossible(cells):
    return abs(cells.count('X') - cells.count('O')) > 1


def check_line(moves_matrix, almost=False):
    x_win = False
    o_win = False
    for i, row in enumerate(moves_matrix):
        if almost:
            if (2 in (row.count('X'), row.count('O'))
                    and row.count(' ')):
                return i, row.index(' ')
            if i == len(row) - 1:
                return None
        if row.count('X') == 3:
            x_win = True
        elif row.count('O') == 3:
            o_win = True
    if x_win != o_win:
        return "X wins" if x_win else "O wins"
    else:
        return "Impossible" if x_win else None


def check_diagonals(matrix_rows, almost=False):
    def check(diagonal):
        if almost:
            if (2 in (diagonal.count('X'), diagonal.count('O'))
                    and diagonal.count(' ')):
                return diagonal.index(' ')
            return None
        x_win = False
        o_win = False
        if diagonal.count('X') == 3:
            x_win = True
        elif diagonal.count('O') == 3:
            o_win = True
        if x_win:
            return "X wins"
        elif o_win:
            return "O wins"
        else:
            return None

    main = [row[i] for i, row in enumerate(matrix_rows)]
    side = [row[i] for i, row in enumerate(matrix_rows[::-1])][::-1]
    win_main = check(main)
    win_side = check(side)
    if almost:
        if isinstance(win_main, int):
            return win_main * 4
        elif isinstance(win_side, int):
            return win_side * 2 + 2
        else:
            return None
    if win_main and win_side:
        return "Impossible"
    else:
        return win_main if win_main else win_side


def has_won(cells):
    row_win = check_line(into_rows(cells))
    col_win = check_line(into_cols(cells))
    diagonal_win = check_diagonals(into_rows(cells))
    wins = (row_win, col_win, diagonal_win)
    if "Impossible" in wins:
        return "Impossible"
    else:
        return row_win or col_win or diagonal_win


def check_state(cells):
    if cells:
        winner = has_won(cells)
        if is_impossible(cells):
            return "Impossible"
        elif winner:
            return winner
        elif is_unfinished(cells):
            return "Game not finished"
        else:
            return "Draw"
    return ''


def coord_to_index(i, j):
    return i + j + (2 - j) * 4


def check_almost(cells):
    row_almost = check_line(into_rows(cells), True)
    if isinstance(row_almost, tuple):
        return row_almost[0] * 3 + row_almost[1]
    col_almost = check_line(into_cols(cells), True)
    if isinstance(col_almost, tuple):
        return col_almost[1] * 3 + col_almost[0]
    diagonal_almost = check_diagonals(into_rows(cells), True)
    if isinstance(diagonal_almost, int):
        return diagonal_almost
    return None


def minimax(cells, symbol, ai_turn=True):
    new_state = check_state(cells)
    if "not finished" in new_state:
        scores = []
        opponent = 'O' if symbol == 'X' else 'X'
        vacancies = [i for i, cell in enumerate(cells) if cell == ' ']
        for i in vacancies:
            new_field = cells[:]
            new_field[i] = symbol
            scores.append(minimax(new_field, opponent, not ai_turn)[0])
        if ai_turn:
            return max(scores), vacancies[scores.index(max(scores))]
        else:
            return min(scores), vacancies[scores.index(min(scores))]
    elif "wins" in new_state:
        return (-10, None) if ai_turn else (10, None)
    else:
        return 0, None


while True:
    user_command = input("Input command:").split()
    if len(user_command) == 3 \
            and user_command[0] == "start" \
            and user_command[1] in ("user", "easy", "medium", "hard") \
            and user_command[2] in ("user", "easy", "medium", "hard"):
        player_one = user_command[1]
        player_two = user_command[2]
        break
    else:
        print("Bad parameters!")
# field = [*input("Enter cells: ")]
field = "_________"
field = [move if move in ('X', 'O', ' ') else ' ' for move in field]
print_field(field)
while True:
    if field.count('O') - field.count('X') < 0:
        next_symbol, next_player = ('O', player_two)
    else:
        next_symbol, next_player = ('X', player_one)
    if next_player == "user":
        new_move = input("Enter coordinates: ").split()
        try:
            new_move = [int(crd) if int(crd) < 4 else False for crd in new_move]
        except ValueError:
            print("You should enter numbers!")
        else:
            if not all(new_move):
                print("Coordinates should be from 1 to 3!")
            elif field[coord_to_index(*new_move)] != ' ':
                print("This cell is occupied! Choose another one!")
            else:
                field[coord_to_index(*new_move)] = next_symbol
    else:
        if next_player == "easy":
            new_move = random.choice([i for i, x in enumerate(field) if x == ' '])
        elif next_player == "medium":
            new_move = check_almost(field)
            if not isinstance(new_move, int):
                new_move = random.choice([i for i, x in enumerate(field) if x == ' '])
        else:
            new_move = minimax(field, next_symbol)[1]
        field[new_move] = next_symbol
        print(f'Making move level "{next_player}"')
    print_field(field)
    game_state = check_state(field)
    if "wins" in game_state or ' ' not in field:
        break
print(game_state)
