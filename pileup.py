from collections import deque

num_testcases = int(raw_input())

for i in range(0, num_testcases):
    num_cubes = int(raw_input())
    cubes = deque(map(int, raw_input().split()))
    possible = "No"
    
    while len(cubes) > 0:
        max_length = max(cubes)
        if cubes[0] == max_length:
            possible = "Yes"
            c = cubes.popleft()
        elif cubes[-1] == max_length:
            possible = "No"
            c = cubes.pop()
        else:
            possible = "No"
            break
            
    print possible
