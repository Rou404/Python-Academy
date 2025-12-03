# Mergand la stanga valoare va scadea, respectiv la dreapta valoarea va creste

counter = 0
pozitie = 50

actiuni = []

"""
R45 -> 45 -> inlocuim "R" cu ""
L1999 -> -1999 -> inlocuim "L" cu - 

transformam in int
"""
""
f = open("input.txt", "r")

for linie in f:
    linie_fara_end = linie.strip()
    linie_fara_R = linie_fara_end.replace("R", "")
    linie_cu_L_minus = linie_fara_R.replace("L", "-")

    actiuni.append(int(linie_cu_L_minus))
print(actiuni)

for actiune in actiuni:
    pozitie = (pozitie + actiune) % 100

    if pozitie == 0:
        counter = counter + 1

print(f"Raspunsul este: {counter}")