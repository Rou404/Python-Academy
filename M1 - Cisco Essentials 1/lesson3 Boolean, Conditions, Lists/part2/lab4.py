# LISTS - Python examples similar to the string demo provided

# Creating lists
lista = [1, 5, 3, 9, 2]
lista_mix = [10, "Python", True, 3.14]
lista_goala = []

print(lista)
print(lista_mix)
print(lista_goala)

# Length of list
print(len(lista))

# Access elements
print(lista[0])      # first element
print(lista[-1])     # last element

# List slicing
print(lista[1:4])    # slice from index 1 to 3
print(lista[:3])     # first 3 elements
print(lista[2:])     # elements from index 2 to end

# Modify elements
lista[0] = 100
print(lista)

# Append, insert, extend
lista.append(50)
print(lista)

lista.insert(2, 999)   # insert at index 2
print(lista)

a = [1, 2, 3]
b = [4, 5, 6]
a.extend(b)           # add all elements from b to a
print(a)

# Remove elements
lista.remove(999)     # removes first occurrence
print(lista)

print(lista.pop())    # pops last element
print(lista)

print(lista.pop(1))   # pops element at index 1
print(lista)

# Delete element by index
del lista[0]
print(lista)

# Clear list
copy_list = lista.copy()
copy_list.clear()
print(copy_list)

# Searching in lists
print(5 in lista)         # True/False
print(lista.count(5))     # count occurrences

# Finding index
lista2 = [10, 20, 30, 40]
print(lista2.index(30))

# Sorting lists
lista_sortare = [5, 1, 7, 3, 8]
lista_sortare.sort()
print(lista_sortare)

lista_sortare.sort(reverse=True)
print(lista_sortare)

# Using sorted() (does not modify list)
print(sorted([9,3,1,4]))

# List comprehension
lista_patrate = [x*x for x in range(1, 6)]
print(lista_patrate)

# Copying lists
lista_original = [1, 2, 3]
lista_copie = lista_original.copy()

print(lista_original)
print(lista_copie)

# Nested lists
matrice = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
print(matrice)
print(matrice[1][2])   # Access element 6

'''
Se citeste de la tastatura lungimea unei liste n,
iar ulterior se citesc n numere pozitive si negative care se adauga in lista,
modifica lista pentru a contine doar elemente pozitive si aratati lista pe ecran 
'''


n = int(input("Introdu lungimea listei: "))
lista = []

for x in range(n):
    numar = int(input("Introdu un numar: "))
    lista.append(numar * numar)

print(lista)




'''
Se citeste de la tastatura lungimea unei liste n,
iar ulterior se citesc n numere pozitive si negative care se adauga in lista,
sa se creeze o copie de lista care contine doar elementele pozitive si aratati lista pe ecran 
'''
 

n = int(input("Introdu lungimea listei: "))
lista = []

for x in range(n):
    numar = int(input("Introdu un numar: "))
    lista.append(numar)

lista_copie_pozitiva = [x for x in lista if x >= 0]
print(lista_copie_pozitiva)


"""
Scrie un program care lucrează cu o listă de numere întregi. Programul trebuie să citească de la tastatură un număr necunoscut de valori, până când utilizatorul introduce cuvântul „stop”.
Dacă utilizatorul introduce altceva decât un număr întreg (inclusiv valori invalide), programul trebuie să afișeze un mesaj de eroare și să ceară din nou inputul, fără să îl adauge în listă.

După ce utilizatorul introduce „stop”, programul trebuie să afișeze următoarele informații despre lista obținută:


lista completă
valoarea minimă
valoarea maximă
media aritmetică a numerelor
suma numerelor
produsul numerelor
lista numerelor pare
lista numerelor impare
câte numere pozitive, negative și zero există
lista sortată crescător
lista sortată descrescător
lista fără duplicate (păstrând ordinea)
o listă nouă care conține pătratul fiecărui număr
o listă în care sunt eliminate toate numerele negative
"""

lista = []

while True:
    x = input("Introdu un numar ('stop' pentru a opri): ")

    if x.lower() == "stop":
        break

    if not x.lstrip("-").isdigit():
        print("Te rog introdu doar numere!")
        continue

    lista.append(int(x))

print("Lista:", lista)
print("Min:", min(lista))
print("Max:", max(lista))
print("Media:", sum(lista) / len(lista))
print("Suma:", sum(lista))

prod = 1
for n in lista:
    prod *= n
print("Produsul:", prod)

pare = [n for n in lista if n % 2 == 0]
impare = [n for n in lista if n % 2 != 0]

pozitive = len([n for n in lista if n > 0])
negative = len([n for n in lista if n < 0])
zerouri = lista.count(0)

print("Pare:", pare)
print("Impare:", impare)
print("Pozitive:", pozitive)
print("Negative:", negative)
print("Zero:", zerouri)
print("Sortata crescator:", sorted(lista))
print("Sortata descrescator:", sorted(lista, reverse=True))

fara_duplicate = []
for n in lista:
    if n not in fara_duplicate:
        fara_duplicate.append(n)
print("Fara duplicate:", fara_duplicate)

patrate = [n*n for n in lista]
print("Patrate:", patrate)

pozitive_only = [n for n in lista if n >= 0]
print("Fara negative:", pozitive_only)
