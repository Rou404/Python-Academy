# Mergand la stanga valoare va scadea, respectiv la dreapta valoarea va creste

actiuni = []

f = open("test.txt", "r")

for line in f:
    actiuni.append(line.strip())

print(actiuni)