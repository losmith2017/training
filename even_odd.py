import sys
import os

# number_entered = int(raw_input("Enter in a integer number: "))

print "This is the name of the script:", sys.argv[0]
print "Number of arguments:", len(sys.argv)
print "The arguments are: ", str(sys.argv)

number_entered = int(sys.argv[1])

if (number_entered % 4) == 0:
	print "{} is a multiple of 4".format(number_entered)
elif (number_entered % 2) == 0:
	print "{} is an even number".format(number_entered)
else:
	print "{} is an odd number".format(number_entered)

exit(0)
