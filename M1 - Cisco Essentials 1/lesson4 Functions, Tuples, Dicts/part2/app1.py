def media(lista):
    m=0
    for v in lista:
        m+=v
    return m/len(lista)

while True:
    try:
        global nr
        nr =int(input('nr elevi: '))
    except Exception:
        print('invalid')
    else:
        break

lista=[]
for i in range(nr):
    while True:
        try:
            varsta=int(input(f"varsta {i+1}: "))
            lista.append(varsta)
        except Exception:
            print('invalid')
        else:
            break

print(f'media este: {media(lista)}')