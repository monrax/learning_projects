import math
import sys


# credit_principal = p
# annuity_payment = a
# count_of_periods = n
# credit_interest = i

def calc_parameter(dict_pars, dict_calc):
    j = 'interest'
    for j in dict_calc:
        if j not in dict_pars:
            param = j
    if param != 'periods':
        i = dict_pars['interest']
        n = dict_pars['periods']
        capital_recovery_f = (i * (1 + i) ** n) / (-1 + (1 + i) ** n)
        dict_pars[param] = dict_calc[param][0](dict_pars, capital_recovery_f)
    else:
        dict_pars[param] = dict_calc[param][0](dict_pars)
    return dict_calc[param][1](dict_pars[param])


def n_str(n):
    years = n // 12
    months = n % 12
    yrs_str = f" {years} year{'s' * (years > 1)} " if years else ''
    mth_str = f" {months} month{'s' * (months > 1)} " if months else ''
    and_str = "and" if years and months else ''
    return "You need" + yrs_str + and_str + mth_str + "to repay this credit!"


def diff_payment(dict_pars, period):
    p = dict_pars['principal']
    n = dict_pars['periods']
    i = dict_pars['interest']
    m = period
    return math.ceil(p / n + i * (p - p * (m - 1) / n))


dict_funcs_a = dict(
    principal=(
        lambda params, crf: math.ceil(params['payment'] // crf),
        lambda p: f"Your credit principal = {p}!"),
    payment=(
        lambda params, crf: math.ceil(params['principal'] * crf),
        lambda a: f"Your annuity payment = {a}!"),
    periods=(
        lambda params: math.ceil(math.log(
            params['payment'] / (params['payment'] - (
                    params['interest'] * params['principal'])),
            1 + params['interest'])
        ),
        lambda n: n_str(n)),
    interest=(lambda i: None, None)
)

args = sys.argv[1:]
dict_args = dict([j.lstrip('-').split('=') if j.startswith("--") else (None, None) for j in args])
if None in dict_args or "type" not in dict_args or len(dict_args) < 4 or "interest" not in dict_args:
    print("Incorrect parameters.")
else:
    calc_type = dict_args.pop("type")
    for parameter in dict_args:
        if parameter == 'interest':
            dict_args[parameter] = float(dict_args[parameter]) / (12 * 100)
        else:
            dict_args[parameter] = math.ceil(float(dict_args[parameter]))
    if [j for j in dict_args.values() if j < 0]:
        print("Incorrect parameters.")
    else:
        if calc_type == "annuity":
            # print(dict_args)
            print(calc_parameter(dict_args, dict_funcs_a))
            print(f"\nOverpayment = {math.ceil(dict_args['payment'] * dict_args['periods'] - dict_args['principal'])}")
        elif calc_type == "diff":
            if "payment" in dict_args:
                print("Incorrect parameters.")
            else:
                overpay = 0
                for j in range(1, dict_args['periods'] + 1):
                    d = diff_payment(dict_args, j)
                    print(f"Month {j}: paid out {d}")
                    overpay += d
                print(f"\nOverpayment = {math.ceil(overpay - dict_args['principal'])}")
        else:
            print("Incorrect parameters.")
