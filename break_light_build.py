def Lbb(x):
	if x >= 56:
		return(True)
	else:
		return(False)
		
def Osection(x):
	return 14
	
number_of_floors = int(raw_input("Enter in number of floors: "))

x = Osection(number_of_floors)

last_floor_good = 0

i = x
while i <= number_of_floors:
	print i, x, last_floor_good
	if not Lbb(i):
		last_floor_good = i
		x = x - 1
		i += x
	else:
		for j in range(last_floor_good + 1, i - 1):
			print j, last_floor_good
			if Lbb(j):
				print j
				break
		break
			

exit(0)
    