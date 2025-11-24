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
Se citeste de la tastatura lungimea unei liste n, iar ulterior se citesc n numere care se adauga in lista, pentru fiecare element din lista, arata patratul lui 
'''







'''
Se citeste de la tastatura lungimea unei liste n,
iar ulterior se citesc n numere care se adauga in lista,
pentru fiecare element din lista, arata patratul lui 
'''







