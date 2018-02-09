import os
import sys
from random import sample

def get_first_last(x_list):
	return[x_list[0], x_list[len(x_list) - 1]]
	
random_list = sample(range(0, 200), 35)

print random_list

print get_first_last(random_list)

# get_first_last(random_list)

exit(0)