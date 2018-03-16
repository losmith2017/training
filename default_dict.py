from collections import defaultdict
d = defaultdict(list)
n,m = raw_input().split(" ")
n = int(n)
m = int(m)
for i in range(0,n):
	d['A'].append(raw_input())
    
for i in range(0,m):
	d['B'].append(raw_input())
	
print d['A']

d['A'][0] = "Seven"

print d['A']

print d['B']

print d
	

positions = []
for i in range(0, len(d['B'])):
	for j in range(0, len(d['A'])):
		# print d['B'][i] d['A'][j]
		if d['B'][i] == d['A'][j]:
			positions.append(str(j+1))
	if len(positions) == 0:
		print "-1"
	else:
		print " ".join(positions)
	positions = []

exit(0)
    