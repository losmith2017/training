from collections import deque

the_queue = deque()

num_oper = int(raw_input())

for i in range(0,num_oper):
    input_line = raw_input().split()
    if len(input_line) > 1:
        getattr(the_queue, input_line[0])(input_line[1])
    else:
        getattr(the_queue, input_line[0])()
    
print " ".join(map(str, the_queue))
        
        
    