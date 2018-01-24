import sys
import os

a = ['20', '7', '45', '-1', '-8', '10', '5', '45', '100', '89', '22', '7', '2', '0']

less_than_choice = int(raw_input("Enter number choice for less than: "))

print [x for x in a if int(x)<less_than_choice]

exit (0)