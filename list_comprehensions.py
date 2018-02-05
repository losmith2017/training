import sys
import os
import random

len_numlist = random.randint(5, 40)

print len_numlist

numlist = []

while len(numlist) < len_numlist:
	numlist.append(random.randint(0, 300))

print numlist

evenlist = [nnn for nnn in numlist if not nnn % 2]

print evenlist

exit (0)