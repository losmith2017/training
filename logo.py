import sys

def count_sort(in_string):
    dlist = dict()
    unique_string = set(in_string)
    for c in unique_string:
		dlist[c] = in_string.count(c)

    sorted_list = [(k, v) for k, v in sorted(dlist.iteritems(), key=lambda(k, v): (-v, k))]
        
    return(sorted_list)
            
    
if __name__ == "__main__":
    s = raw_input().strip()
    
    letter_dict = count_sort(s)

    for i in range(3):
        print " ".join(map(str, letter_dict[i]))