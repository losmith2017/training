from collections import OrderedDict

num_lines = int(raw_input())

word_list_count = OrderedDict()

for i in range(0, num_lines):
	w = raw_input()
	if w in word_list_count:
		word_list_count[w] += 1
	else:
		word_list_count[w] = 1
		
print str(len(word_list_count))

count_list = []
for w in word_list_count:
	count_list.append(word_list_count[w])
	
print " ".join(map(str, count_list))
	