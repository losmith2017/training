import sys
import os

a = []

while True:

	x = raw_input("Input an integer, or enter q to quit: ")
	
	if (x == 'q') or (x == 'Q'):
		break
	try:
		x_int = int(x)

	except ValueError:
		print "ERROR: Not an integer. Try again..."
		continue
		
	a.append(x_int)
	
		
under_ten = []

for element in a:
	if element < 10:
		under_ten.append(element)

if len(under_ten) == 0:
	message =  "Nothing in the list is than than 10"
else:
	message = "List of integers less than ten are:"
	for element in under_ten:
		message = message + " " + str(element)

print message

exit(0)