import os
import sys

def get_integer(the_prompt):
	x =  raw_input(the_prompt)
	try:
		x = int(x)
	except ValueError:
		print ("ERROR: Not an integer")
		exit (1)
		
	return (x)
	
def is_prime(x):
	the_divisors = []
	for nnn in range(1, abs(x) + 1):
		if x % nnn == 0:
			the_divisors.append(nnn)
	
	if len(the_divisors) == 2:
		return("true")
	else:
		return("false")


potential_prime = get_integer("Please enter in a potential prime number: ")

if is_prime(potential_prime) == "true":
	print str(potential_prime) + " is a prime number"
else:
	print str(potential_prime) + " is not a prime number"
	
	
exit (0)