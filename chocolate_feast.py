import sys

def chocolateFeast(n, c, m):
    num_of_chocolates = int(n / c)
    num_wrappers = num_of_chocolates
    while num_wrappers >= m:
        additional_chocolates = int(num_wrappers / m)
        num_wrappers_traded = additional_chocolates * m
        num_of_chocolates += additional_chocolates
        num_wrappers = num_wrappers - num_wrappers_traded + additional_chocolates
 
    return(num_of_chocolates)

if __name__ == "__main__":
    t = int(raw_input().strip())
    for a0 in xrange(t):
        n, c, m = raw_input().strip().split(' ')
        n, c, m = [int(n), int(c), int(m)]
        result = chocolateFeast(n, c, m)
        print result
