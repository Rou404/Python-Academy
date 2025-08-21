sir = """In primavara anului 1894, toata Londra a fost interesata, iar lumea la moda a fost consternata de
uciderea onorabilului Ronald Adair in circumstante cele mai neobisnuite si inexplicabile. Publicul
a aflat deja acele detalii ale crimei care au iesit la iveala in ancheta politiei; dar multe au fost
suprimate cu acea ocazie, deoarece cazul acuzarii era atat de coplesitor de puternic, incat nu era
necesar sa se prezinte toate faptele. Abia acum, la sfarsitul a aproape zece ani, imi este permis sa
aprovizionez acele verigi lipsa care alcatuiesc intregul lant remarcabil. Crima era interesanta in sine, dar acel interes nu era nimic pentru mine in comparatie cu continuarea de neconceput, care
mi-a oferit cel mai mare soc si surpriza din orice eveniment din vitța mea aventuroasa. Chiar si
acum, dupa acest interval lung, mă trezesc emotionat cand ma gandesc la asta si simt din nou acel
potop brusc de bucurie, uimire si neincredere care mi-a cufundat cu totul mintea."""


def count_letter(l):
    count = 0
    for letter in sir:
        if letter == l: count += 1
    print(count)


def select_word(words):
    for word in words:
        if word.startswith( 's'): print(word)


l = input("Introdu o litera: ")
count_letter(l)
words = sir.split(' ')
select_word(words)