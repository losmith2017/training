# My Quicksorting

def quicksorting(l):

	if len(l) < 2:
		return(l)
		
	left = []
	right = []
	equal = []
	pivot = l[0]
	equal.append(pivot)

	for i in l[1:]:
		if pivot > i:
			left.append(i)
		elif pivot < i:
			right.append(i)
		else:
			equal.append(i)
		
	newlist = quicksorting(left) + equal + quicksorting(right)
	
	return(newlist)



if __name__ == "__main__":
	f = open("C:\Users\louan\Git\my_project\my_quicksort_input.txt", 'r')
	
	int_list = map(int, (f.read().split()))
	
	result = quicksorting(int_list)
	
	print int_list
	
	print result
	
	f.close()