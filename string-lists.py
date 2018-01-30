import sys
import os

input_string = raw_input("Enter in a string to test if it is a palindrome: ")

reverse_string = input_string[len(input_string)-1::-1]

# i = len(input_string) - 1

# while i >= 0:
#	reverse_string = reverse_string + input_string[i]
#	i -= 1

	
if input_string == reverse_string:
	print 'The string "{}" is a palindrome'.format(input_string)
else:
	print 'The string "{}" is NOT a palindrome'.format(input_string)
	
exit (0)