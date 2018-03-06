def print_rangoli(size):
	alphastring = "abcdefghijklmnopqrstuvwxyz"
	
	nline = []
	seeline = []
	for i in range(size):
		s = "-".join(alphastring[i:size])
		nline.append((s[::-1]+s[1:]).center(4*size-3, "-"))
	print ('\n'.join(nline[:0:-1]+nline))


if __name__ == '__main__':
	n = int(raw_input())
	print_rangoli(n)
	