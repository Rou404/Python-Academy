text = "  Python               este un limbaj puternic!  "
word = "Python"

print(len(text))           # Lungimea totală a șirului (inclusiv spațiile)

print(text)
print(text.strip())        # Elimină spațiile din ambele capete
print(text.lstrip())       # Elimină spațiile din stânga
print(text.rstrip())       # Elimină spațiile din dreapta


print(word.lower())        # python
print(word.upper())        # PYTHON

print("abc".isalpha())     # True – doar litere
print("1230".isdigit())     # True – doar cifre
print("abc123".isalnum())  # True – doar litere și cifre
print("                ".isspace())     # True – doar spații

print("python este tare".capitalize())   # Prima literă mare
print("python este tare".title())        # Fiecare cuvânt cu prima literă mare

print(word.startswith("Py"))    # True
print(word.endswith("on"))      # True

print(text.find("limbaj"))      # Returnează indexul de început (sau -1 dacă nu există)
print(text.index("Python"))     # Returnează indexul de început (eroare dacă nu există)

print(text.replace("Python", "C++"))   # Înlocuiește toate aparițiile

print(text.count(" "))          # Numărul de apariții ale caracterului 't'

cuvinte = text.split()          # Împarte textul în listă de cuvinte (după spațiu)
print(cuvinte)
print("".join(cuvinte))        # Unește lista de cuvinte într-un șir, cu separatorul "_"

print("PyThOn".swapcase())      # Inversează majuscule/minuscule

print(word.center(20, "-"))     # Centrează textul într-un spațiu de 20 caractere
print(word.ljust(20, "!"))      # Aliniază la stânga
print(word.rjust(20, "|"))      # Aliniază la dreapta
    
print("Python" in text)        # True – verifică dacă textul conține subșirul
print("Java" not in text)      # True – verifică dacă NU conține

print(ord('N'))                # Codul ASCII al caracterului 'A'
print(chr(31))                 # Caracterul pentru codul 66 (=> 'B')

print("PYTHON".isupper())      # True
print("python".islower())      # True

print(text.strip().lower().capitalize())  # Combinație de funcții
x = True
y = False

if x:
    pass
elif y:
    pass
else:   
    pass


"""
E1

Scrie un program care citește un număr de la tastatură și afișează:
 
"Număr pozitiv" dacă este mai mare ca 0,
 
"Număr negativ" dacă este mai mic ca 0,
 
"Numărul este zero" în rest.

"""

numar = int(input("Introdu un numar: "))

if numar > 0:
    print("Numarul este pozitiv")
elif numar < 0:
    print("Numarul este negativ")
else:
    print("Numarul este 0")

 
'''
E2
 
Citește un număr de la tastatură și verifică dacă este par sau impar.
Hint: folosește operatorul %.
 
'''

numar = int(input("Introdu un numar: "))

if numar % 2 == 0:
    print("Numarul este par")
else:
    print("Numarul este impar")


'''
E3
 
Scrie un program care:
 
Cere utilizatorului să introducă o propoziție.
 
Transformă propoziția într-o listă de cuvinte, folosind metoda split().
 
Afișează lista obținută.
 
Apoi reconstruiește propoziția, dar cu liniuțe (-) între cuvinte, folosind join().
 
Afișează noul șir rezultat.


'''

sirul_meu = input()

sirul_meu = sirul_meu.split()

print(sirul_meu)

sirul_meu = "-".join(sirul_meu)

print(sirul_meu)


'''
E4
 
Citește un caracter de la tastatură și verifică: 
 
dacă s-a introdus exact un singur caracter, contrar -> "Trebuie introdus un singur carcter {sirul_introdus} nu este un singur caracter"
 
dacă este un spațiu → "Caracterul {char_introdus} este spațiu"
dacă este literă sau cifră ->	 "Caracterul {char_introdus} este alfanumeric"
altfel → "Caracterul {char_introdus} este alt tip de caracter"		
'''

caracterul_meu = input()

if len(caracterul_meu) > 1:
    print(f"Trebuie introdus un singur caracter, {caracterul_meu} nu este un singur caracter")
elif caracterul_meu.isspace():
    print(f"Caracterul {caracterul_meu} este spatiu")
elif caracterul_meu.isalnum():
    print(f"Caracterul {caracterul_meu} este alfanumeric")
else:
    print(f"Caracterul {caracterul_meu} este alt tip de caracter")