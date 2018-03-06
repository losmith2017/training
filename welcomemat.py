N, M = map(int,raw_input().split()) # More than 6 lines of code will result in 0 score. Blank lines are not counted.
if (N % 2 == 0) or (M % N == 1): exit(1)
for i in xrange(1,N,2): 
	print "-"*((M-len(".|.")*i)/2) + ".|."*i + "-"*((M-len(".|.")*i)/2)
print "-"*((M-len("WELCOME"))/2) + "WELCOME" + "-"*((M-len("WELCOME"))/2)
for i in xrange(N-2,-1,-2): 
	print "-"*((M-len(".|.")*i)/2) + ".|."*i + "-"*((M-len(".|.")*i)/2)
	
print ""

if (N % 2 == 0) or (M % N == 1): exit(1)
for i in xrange(1,N,2): 
	print (".|."*i).center(M, "-")
print ("WELCOME").center(M, "-")
for i in xrange(N-2,-1,-2): 
	print (".|."*i).center(M, "-")