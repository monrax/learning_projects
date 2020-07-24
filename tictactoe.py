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


def check_line(moves_matrix):
    x_win = False
    o_win = False
    for row in moves_matrix:
        if row.count('X') == 3:
            x_win = True
        elif row.count('O') == 3:
            o_win = True
    if x_win != o_win:
        return "X wins" if x_win else "O wins"
    else:
        return "Impossible" if x_win else None


def check_diagonals(matrix_rows):
    def check(diagonal):
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
    side = [row[i] for i, row in enumerate(matrix_rows[::-1])]
    win_main = check(main)
    win_side = check(side)
    if win_main and win_side:
        return "Impossible"
    else:
        return win_main if win_main else win_side


def has_won(cells):
    row_win = check_line(into_rows(cells))
    col_win = check_line(into_cols(cells))
    diagonal_win = check_diagonals(into_rows(cells))
    wins = (row_win, col_win, diagonal_win)
    if "Impossible" in wins or wins.count(None) < 2:
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


# new_field = [*input("Enter cells: ")]
field = "_________"
field = [move if move in ('X', 'O', ' ') else ' ' for move in field]
print_field(field)
while True:
    next_symbol = 'O' if field.count('O') - field.count('X') < 0 else 'X'
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
            game_state = check_state(field)
            print_field(field)
            if "wins" in game_state or ' ' not in field:
                break
print(game_state)
