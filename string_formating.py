def print_formatted(number):

	len_bin = len("{0:b}".format(number))
	for i in range(1,number+1):
		print "{0:{width}d} {0:{width}o} {0:{width}X} {0:{width}b}".format(i,width=len_bin)
		

if __name__ == '__main__':
	n = int(raw_input())
	print_formatted(n)