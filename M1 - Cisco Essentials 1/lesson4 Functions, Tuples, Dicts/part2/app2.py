def suma(lista: list):
    return sum(lista)

def medie(lista: list):
    return sum(lista)/len(lista)

def putere(lista: list):
    return [i**2 for i in lista]


meniu = {
    "1": medie,
    "2": suma,
    "3": putere
    }

print("Introduceti numere. Cand sunteti gata, introduceti x.")

lista = []

while True:
    n = input("Numar: ")
    if n == 'x':
        break
    lista.append(float(n))

print("""Meniu:
1. Media numerelor
2. Suma numerelor
3. Puterea numerelor din lista de numere
4. Iesire""")

while True:
    opt = input("introduceti optiunnea dvs: ")

    if opt in meniu.keys():
        print(meniu[opt](lista))
    elif opt == '4':
        print("Iesire")
        break