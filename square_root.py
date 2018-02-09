#!/usr/bin/env pythonimport

import math
import sys

inputed_numbers = sys.argv[1].split(",")

end_values = []

c = 50

h = 30

for x in inputed_numbers:
	print x
	end_values.append(str(int(round(math.sqrt(2*c*float(x)/h)))))
	
print end_values

exit(0)
	
	