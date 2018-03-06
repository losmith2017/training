def merge_the_tools(string, k):
	n = len(string)
	u = []
	if not n % k == 0:
		print "ERROR: " + str(k) + " is not a factor of string length " + str(len(string))

	for i in range(0, len(string), k):
		t = string[i:i+k]
		u = []
		for x in t:
			if x not in u:
				u.append(x)
		print ''.join(u)
		
if __name__ == '__main__':
	string, k = "AABCAAADA", 3
	merge_the_tools(string, k)