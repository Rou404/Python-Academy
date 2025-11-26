lista = [1,2,3]

#Functii
print()
input()
lista.append()
str()
int()

lista = [1,2,3]
print(lista)

def este_par(numar : int):
    lista.append(1)
    rezultat = numar % 2 == 0
    return rezultat

rezultat = este_par(5)
print(rezultat)


var1 = 0

def sum_numbers(number_a, number_b):
    global var1
    var1 = var1 + 1
    result = number_a + number_b + var1
    return result

result1 = sum_numbers(10, 20)
print(var1)
result2 = sum_numbers(10, 20)
print(var1)
result3 = sum_numbers(10, 20)
print(var1)


def get_numbers():
    lista = []

    while True:
        x = input("Introdu un numar ('stop' pentru a opri): ")

        if x.lower() == "stop":
            break

        if not x.lstrip("-").isdigit():
            print("Te rog introdu doar numere!")
            continue

        lista.append(int(x))

    return lista

def basic_stats(lista):
    minim = min(lista)
    maxim = max(lista)
    media = sum(lista) / len(lista)
    suma = sum(lista)

    prod = 1
    for n in lista:
        prod *= n

    return minim, maxim, media, suma, prod    
    
def categorize_numbers(lista):
    pare = [n for n in lista if n % 2 == 0]
    impare = [n for n in lista if n % 2 != 0]
    pozitive = len([n for n in lista if n > 0])
    negative = len([n for n in lista if n < 0])
    zerouri = lista.count(0)

    return pare, impare, pozitive, negative, zerouri

def sorting_and_unique(lista):
    sort_cresc = sorted(lista)
    sort_desc = sorted(lista, reverse=True)

    fara_duplicate = []
    for n in lista:
        if n not in fara_duplicate:
            fara_duplicate.append(n)

    return sort_cresc, sort_desc, fara_duplicate

def transformations(lista):
    patrate = [n*n for n in lista]
    pozitive_only = [n for n in lista if n >= 0]

    return patrate, pozitive_only

def main():
    lista = get_numbers()

    print("Lista", lista)

    minimum, maximum, media, suma, produs = basic_stats(lista)
    print("Min:", minimum)
    print("Max:", maximum)
    print("Suma:", suma)
    print("Media:", media)
    print("Produs:", produs)

    pare, impare, pozitive, negative, zerouri = categorize_numbers(lista)
    print("Pare:", pare)
    print("Impare:", impare)
    print("Pozitive:", pozitive)
    print("Negative:", negative)
    print("Zero:", zerouri)

    sort_cresc, sort_desc, fara_duplicate = sorting_and_unique(lista)
    print("Sortata crescator:", sort_cresc)
    print("Sortata descrescator:", sort_desc)
    print("Fara duplicate", fara_duplicate)

    patrate, pozitive_only = transformations(lista)
    print("Patrate:", patrate)
    print("Fara negative:", pozitive_only)

main()
