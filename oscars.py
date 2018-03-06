# Oscar Random Choices
from random import randint

f = open('C:\Users\louan\Git\my_project\oscar_input.txt', 'r')

movies = []

while 1:
	oscar_group = f.readline().split()
	if not oscar_group : break
	oscar_category = " ".join(oscar_group[0:len(oscar_group)-1])
	num_entries = int(oscar_group[len(oscar_group)-1])
	movies = []
	for i in range(0,num_entries):
		movies.append(f.readline())
		if not movies[i] : break
	print oscar_category + " - " + movies[randint(0, num_entries-1)]
	
f.close()

	
