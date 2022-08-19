from random import randint

list_prints = []


def print_one_time(text):
    while True:
        if text in list_prints:
            break
        else:
            print(text + "\n")
            list_prints.append(text)
            break




while True:
    #print("OOi")
    print_one_time("Printou uma vez")
    print_one_time("Printou outra coisa")
    print("Teste")

