# https://www.hackerrank.com/challenges/service-lane/problem

import sys

def serviceLane(w, cases):
    result = []
    for item in cases:
        result.append(min(w[item[0]:item[1]+1]))
    return result

if __name__ == "__main__":
    n, t = raw_input().strip().split(' ')
    n, t = [int(n), int(t)]
    width = map(int, raw_input().strip().split(' '))
    cases = []
    for cases_i in xrange(t):
        cases_temp = map(int,raw_input().strip().split(' '))
        cases.append(cases_temp)
    result = serviceLane(width, cases)
    print "\n".join(map(str, result))
