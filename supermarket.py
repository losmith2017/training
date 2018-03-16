from collections import OrderedDict

num_items = int(raw_input())
ordered_items = OrderedDict()

for i in range(0,num_items):
	input_item_line = raw_input().split()
	item_string = []
	for w in input_item_line:
		if w.isdigit():
			netcost = int(w)
			break
		else:
			item_string.append(w)
	item = " ".join(item_string)
	if item in ordered_items:
		ordered_items[item] += netcost
	else:
		ordered_items[item] = netcost
		
for item in ordered_items:
	print item + " " + str(ordered_items[item])
	
