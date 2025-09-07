# salarii = [int(x) for x in input(f"Introduceti salariile: ").split(",")]
# procent = int(input("Introduceti procentul de marire"))
#
#
# calcul = list(map(lambda s: s + s*(procent/100), salarii))
# print(calcul)

import datetime

date1 = datetime.datetime(2020, 10, 10)
date2 = datetime.datetime(2020, 10, 8)

# Comparison of datetime objects (later date is greater)
print(" Is date1 greater than date2?",date1 > date2)

# Get current date and time
date_now = datetime.datetime.now()
print("Current date and time:", date_now)

# Calculate the difference between two dates (result is a timedelta object)
difference = date_now - date1
print("Difference between now and date1:", difference.days)
print("Type of difference:", type(difference))