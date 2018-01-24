import sys
import os
import datetime

def main():

	current_year = int(datetime.date.today().strftime("%Y"))
	
	name = raw_input("Please enter your name: ")

	age = int(raw_input("How old will you be in current_year: "))
	
	repeat_message_count = int(raw_input("Please enter the number of times to repeat message: "))

	current_year = int(datetime.date.today().strftime("%Y"))
	
	num_of_years_until_100 = 100 - age
	
	year_to_turn_100 = str(current_year + num_of_years_until_100)
	
	message = name + " will turn 100 years of age in the year " + year_to_turn_100
	
	i = 0
	while i < repeat_message_count:
		print message
		i += 1

	return 0

if __name__ == "__main__":
    pname = os.path.basename(sys.argv[0])
    main()		