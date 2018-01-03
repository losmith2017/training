import argparse
import os
import sys

def main():

	tmax=100
	nmax=100
	
	input_tests=os.path.abspath("C:\Users\louan\Git\my_project\chocolate_input.txt")
	f = open(input_tests, 'r')

	A = []
	T = int(f.readline())
	
	if (T > tmax) or (T < 1):
		print "ERROR: The number of test cases must be greater than 0 and less than 100"
		return

	print 'Number of test cases', T, '\n'
	i = 0
	while (i < T):
		N = int(f.readline())
		
		if (N > nmax) or (T < 1):
			print "ERROR: The number of packets must be greater than 0 and less than 100"
			return 1
		
		packet_line=f.readline()
		
		A = map(int, packet_line.split())
		
		if len(A) != N:
			print '\nERROR: The number integers in line do not equal', N
			print '\t', A
			return 1
			
		m = int(f.readline())
		
		if (m < 1) or (m > 100):
			print '\nERROR: The number of students must be greater than 0 and less than 100'
			return 1
		
		if (len(A) != len(filter(lambda x: x > 0, A))) or (len(A) != len(filter(lambda x: x <= 100, A))):
			print '\nERROR: The number of items in the packets are either less than 1 or greater than 100', A
			return 1
			
		A_Sort=sorted(A)
		
		j = 0
		k = m - 1
		min_diff = None
		while k < len(A_Sort):
			new_min_diff = A_Sort[k] - A_Sort[j]
			if min_diff is None:
				min_diff = new_min_diff
				student_list = A_Sort[j:m+j]
			if new_min_diff < min_diff:
				min_diff = new_min_diff
				student_list = A_Sort[j:m+j]
			j += 1
			k = j + m - 1
				
		print '\nAvailable packets ', N
		print 'Number of Students ', m
		
		outstring1 = 'We can pick'
		j = 0
		while j < len(student_list) - 1:
			outstring1 = outstring1 + ' ' + str(student_list[j])
			j += 1
		outstring1 = outstring1 + ' and ' + str(student_list[j])
		print outstring1, 'and get the minimum'
		print 'difference between maximum and minimum packet'
		print 'sizes. ie {} - {} = {}'.format(student_list[len(student_list)-1], student_list[0], min_diff)
		i += 1
		
	if (f.readline() != ''):
		print '\nERROR: Not at end of file, there should not be more than', T, 'tests.'
		
	f.close()
	
	return 0
			
if __name__ == "__main__":
    pname = os.path.basename(sys.argv[0])
    main()		
