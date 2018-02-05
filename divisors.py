#! /usr/bin/python2.7

import sys
import os

the_number = int(raw_input("Enter integer: "))

message = "List of numbers that divide into " + str(the_number) + " are:"


for x in range(1,the_number+1):
	if the_number % x == 0:
		message = message + " " + str(x)
		
print message
		
exit (0)
