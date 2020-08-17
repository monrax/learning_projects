import random


def who_beats(choice, options):
    choice_index = options.index(choice)
    half_len = len(options) // 2
    if choice_index < half_len:
        ans = options[choice_index + 1: choice_index + 1 + half_len]
    else:
        leftover = options[choice_index + 1:]
        ans = leftover + options[:half_len - len(leftover)]
    return ans


rating_file = open("rating.txt", 'r')
scores = [line.split() for line in rating_file.readlines()]
rating_file.close()
scores = {i[0]: int(i[1]) for i in scores}

user_name = input("Enter your name:")
user_score = scores.setdefault(user_name, 0)
print("Hello,", user_name)

choices = input()
if not choices:
    choices = ["rock", "paper", "scissors"]
else:
    choices = choices.split(',')
beat_choice = {i: who_beats(i, choices) for i in choices}
print("Okay, let's start")

while True:
    user_choice = input().strip()
    if user_choice in choices:
        cpu_choice = random.choice(choices)
        if user_choice == cpu_choice:  # draw
            user_score += 50
            print(f"There is a draw ({cpu_choice})")
        elif user_choice in beat_choice[cpu_choice]:  # win
            user_score += 100
            print(f"Well done. Computer chose {cpu_choice} and failed")
        else:  # lose
            print("Sorry, but computer chose", cpu_choice)
    elif user_choice == "!rating":
        print("Your rating:", user_score)
    elif user_choice == "!exit":
        break
    else:
        print("Invalid input")

scores[user_name] = user_score
rating_file = open("rating.txt", 'w')
for name, score in scores.items():
    print(name, score, file=rating_file)
rating_file.close()

print("Bye!")
