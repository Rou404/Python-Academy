'''
E1
Se citeste un numar n de la tastatura, afiseaza fiecare numar par de la 1 la n
 
 
Exemplu pentru n = 10
 
Output:
2
4
6
8
10
'''

n = int(input("Introdu un numar: "))

for numar in range(1, n + 1):
    if numar % 2 == 0:
        print(numar)

'''
E1.2
 
Se citeste un numar n si m de la tastatura, afiseaza fiecare numar divizibil cu m de la 1 la n
 
Exemplu pentru n = 16, m = 8
 
Output:
8
16
 
'''

n = int(input("Introdu un numar: "))
m = int(input("Introdu un numar: "))

for numar in range(1, n + 1):
    if numar % 2 == 0 and numar % m == 0:
        print(numar)


'''
E2
 
Se citeste un numar n de la tastatura, afiseaza suma fiecarui numar de la 1 la n.
 
Exemplu pentru n = 10
Output:
55
'''
 
n = int(input("Introdu un numar: "))

suma = 0

for numar in range(1, n + 1):
    suma += numar # echivalent cu suma = suma + numar

print(suma)

'''
E3

Se citeste un sir de caractere de la tastatura, sa se afiseze numarul de vocale din sir.
 
Exemplu pentru sir = "Python este un limbaj"
Output: 
6
 
'''

vocale = "aeiou"
count = 0

sir = input("Introdu un text: ")

for litera in sir:
    if litera.lower() in vocale:
        count += 1

print(count)


'''
Exercitiu extra (tema de casa in caz ca nu s-a terminat)

Să creezi un mic program care simulează funcționarea unui ATM (bancomat). Programul trebuie:
 
Să pornească cu un sold inițial (de exemplu 0 sau 1000).
 
Să folosească un loop infinit (while True) ca să întrebe utilizatorul ce vrea să facă.
 
Utilizatorul poate alege:
 
1 — Depunere
 
2 — Retragere
 
3 — Afișare sold
 
4 — Ieșire din program
 
Programul trebuie să actualizeze soldul în funcție de acțiuni.
 
Programul trebuie să verifice erorile (ex.: nu poți retrage mai mult decât ai) si sa afiseze un mesaj pentru fiecare operatie

'''

sold=1000
pin=1234
incercari=2
auth=False
upin=int(input('introdu pin: '))
while incercari:
    if upin==pin:
        auth=True
        break
    else:
        print('pin gresit')
        upin=int(input('introdu pin: '))
        incercari=incercari-1
 
if auth==False:
    print('Nu mai ai incercari')
 
 
 
while auth:
    actiune=int(input('''Alege o actiune:
                      1-Depunere
                      2-Retragere
                      3-Afisare sold
                      4-Iesire in program
                       '''))
    if actiune==1:
        suma=int(input('Introdu suma pe care vrei sa o depui: '))
        sold=sold+suma
        print(f'Sold: {sold} lei')
    if actiune==2:
        suma=int(input('Introdu suma pe care vrei sa o retragi: '))
        if suma>sold:
            print('Nu ai destui bani')
        else:
            sold=sold-suma
            print(f"Sold: {sold} lei")
 
    if actiune==3:
        print(sold)
    if actiune==4:
        print('O zi buna!')
        break

