def check_char_pair(pair):
    r, i = pair
    return bool(not r or (r == '.' and i) or r == i)


def check_same_len(reg, inp):
    if reg and inp:
        return all(map(check_char_pair, zip(reg, inp)))
    else:
        return check_char_pair((reg, inp))


def check_dif_len(reg, inp):
    len_dif = len(inp) - len(reg)
    if len_dif >= 0:
        for i in range(len_dif+1):
            if check_same_len(reg, inp[i:i+len(reg)]):
                return True
    return False

  
def remove_pre_mark(expr, mark):
    new_expr = list(expr)
    for _ in range(expr.count(mark)):
        if new_expr[0] != mark:
            new_expr.pop(new_expr.index(mark)-1)
            new_expr.remove(mark)
    return ''.join(new_expr)


def no_rep(reg_expr, inp_expr, mark):
    character = reg_expr[reg_expr.index(mark) - 1]
    if character == '.':
        len_dif = len(inp_expr) - len(reg_expr) + 1
        return reg_expr.replace(mark, '.' * len_dif), inp_expr
    else:
        first_char = ''
        last_char = ''
        if inp_expr[0] == character:
            first_char = character
        if inp_expr[-1] == character:
            last_char = character
        return reg_expr.replace(mark, ''), first_char + character.join(filter(bool, inp_expr.split(character))) + last_char


def possibles(rx, ix):
    def update_no_qmark(possib_list, mark):
        nonlocal rx, ix
        pos = possib_list[:]
        if pos:
            aux = [tuple(map(lambda x: no_rep(*x, mark), pos))]
            if mark !='+':
                aux.append(tuple(map(lambda x: (remove_pre_mark(x[0], mark), x[1]), pos)))
            for n in aux:
                pos.extend(n)
        if mark != '+':
            pos.append((remove_pre_mark(rx, mark), ix))
        pos.append(no_rep(rx, ix, mark))
        return pos
        
    if '?' in rx:
        possib = [(rx.replace('?',''), ix), (remove_pre_mark(rx, '?'), ix)]
        if '*' in rx:
            possib = update_no_qmark(possib, '*')
            if '+' in rx:
                possib = update_no_qmark(possib, '+')
        elif '+' in rx:
            possib = update_no_qmark(possib, '+')
    elif '*' in rx:
        possib = update_no_qmark([], '*')
        if '+' in rx:
            possib = update_no_qmark(possib, '+')
    elif '+' in rx:
        possib = update_no_qmark([], '+')
    else:
        possib = [(rx, ix)]
    return possib

def no_escaped(regx):
    x = list(regx)
    esc_chars = []
    for i, c in enumerate(x):
        if c == '\\' and i < len(x) - 1:
            if x[i + 1] in '?.*+':
                esc_chars.append(x.pop(i + 1))
            else:
                esc_chars.append('')
    return ''.join(x), esc_chars

def escaped_chars_back(escaped_chars_list, possibles_list):
    if escaped_chars_list:
        new_pos_list = []
        for pos in possibles_list:
            r = list(pos[0])
            for c in escaped_chars_list:
                if c:
                    r[r.index('\\')] = c
            new_pos_list.append((''.join(r), pos[1]))
        return new_pos_list
    else:
        return possibles_list

def check_regex(rx, ix):       
    if rx:
        ix = ix.split()
        escaped = []
        if '\\' in rx:
            rx = rx.replace('\\\\','\\')
            rx, escaped = no_escaped(rx)
        if rx[0] == '^' and rx[-1] == "$":
            first_possib = escaped_chars_back(escaped, possibles(rx[1:-1], ix[0]))
            last_possib = escaped_chars_back(escaped, possibles(rx[1:-1], ix[-1]))
            first = any(map(lambda x: check_same_len(x[0], x[1][:len(x[0])]), first_possib))
            last = any(map(lambda x: check_same_len(x[0], x[1][-len(x[0]):]), last_possib))
            return first and last
        elif rx[0] == '^':
            possib = escaped_chars_back(escaped, possibles(rx[1:], ix[0]))
            return any(map(lambda x: check_same_len(x[0], x[1][:len(x[0])]), possib))
        elif rx[-1] == '$':
            possib = escaped_chars_back(escaped, possibles(rx[:-1], ix[-1]))
            return any(map(lambda x: check_same_len(x[0], x[1][-len(x[0]):]), possib))
        else:
            return any(any(map(lambda x: check_dif_len(x[0], x[1]), escaped_chars_back(escaped, possibles(rx, input_word)))) for input_word in ix)
    else:
        return True

x,y = input().split('|')
print(check_regex(x,y))
