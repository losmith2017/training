#! /usr/bin/python2.7

import sys
import os
from random import randint


num_elements_a = 25
num_elements_b = 35

a = []
b = []

i = 0
while i <= num_elements_a:
	a.append(randint(0, 150))
	i += 1
	
	
i = 0
while i <= num_elements_b:
	b.append(randint(0, 150))
	i += 1
	
	
common_list = []

for num_a in a:
	if num_a in b:
		if not num_a in common_list:
			common_list.append(num_a)
			
print a
print b

print "Common numbers in two list are: " + ' '.join(map(str,common_list))
		
# common_set = set([x for x in a if x in b])
# common_list_2 = list(common_set)

# print common_list_2

exit ()
