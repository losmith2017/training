def minion_game(string):
	string = string.upper()
	stuart_score = 0
	kevin_score = 0
	for string_count in range(0,len(string)):
		if not string[string_count] in "AEIOU":
			stuart_score += len(string) - string_count
			print "Stuart", string[string_count], str(len(string)), str(string_count), stuart_score
		else:
			kevin_score += len(string) - string_count
			print "Kevin", string[string_count], str(len(string)), str(string_count), kevin_score
			
	if stuart_score > kevin_score:
		print "Stuart " + str(stuart_score)
	elif kevin_score > stuart_score:
		print "Kevin " + str(kevin_score)
	else:
		print "Draw"
				
		
if __name__ == '__main__':
	s = "banana"
	minion_game(s)