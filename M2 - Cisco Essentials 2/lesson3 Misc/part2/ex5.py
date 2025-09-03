import os

useri = []
with open("user.txt", "rt") as file:
    for line in file:
        result = useri.append(line.replace('\n', '').split(';'))

filtru = list(filter(lambda user: user[1] == os.name, useri))

print(filtru)