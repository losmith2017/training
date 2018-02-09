import sys
import os
from random import sample


num_elements_a = 20
num_elements_b = 25 

a = sample(range(0, 100), num_elements_a)
b = sample(range(0, 100), num_elements_b)
	
common_list = set([x for x in a if x in b])

print "Common numbers in two list are: " + ' '.join(map(str,common_list))

exit ()
