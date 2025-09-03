import datetime

data_nastere=input('Data nasterii in formatul YYYY-M-D [q pentru a iesi]: ')
data_nastere=datetime.datetime.strptime(data_nastere,'%Y-%m-%d')
print(f'Ai {(datetime.datetime.now()-data_nastere).days} zile pe acest pamant.')
data=datetime.datetime(datetime.datetime.now().year,data_nastere.month,data_nastere.day)
data_viitoare=(data-datetime.datetime.now()).days
if data_viitoare<30:
    print(f'Imediat va fi ziua ta! Mai {data_viitoare} zile.')
else:
    print(data_viitoare)