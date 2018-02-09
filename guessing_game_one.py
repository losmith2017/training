import sys
import os
from random import randint

ran_number = randint(1, 9)

num_tries = 0

while (1):

	guessed_number = raw_input("Guess a number from 1 to 9, or type exit to quit: ")
	
	if guessed_number.lower() == "exit":
		print "Game is finished"
		break

	try:
		x_guessed = int(guessed_number)
	except ValueError:
		print "ERROR: Not an integer. Try again..."
		continue
		
	if x_guessed < 1 or x_guessed > 9:
		print "ERROR: the number should be between 1 and 9"
		continue
			
	if x_guessed == ran_number:
		print "Correct! You guessed number after " + str(num_tries) + " tries"
		print "Try again..."
		num_tries = 0
		ran_number = randint(1, 9)
	elif x_guessed < ran_number:
		print "You guessed too low"
		num_tries += 1
	elif x_guessed > ran_number:
		print "You guessed too high"
		num_tries += 1
			
exit (0)
			
		
			