import sys
import os

allowed_entries = ["rock", "scissors", "paper"]

while (1):
	player_one = raw_input("Player One - enter rock, paper or scissors: ").lower()
	
	while player_one not in allowed_entries:
		print "ERROR: Wrong Entry " + player_one
		player_one = raw_input("Player One - enter rock, paper or scissors: ").lower()
		
	player_two = raw_input("Player Two - enter rock, paper or scissors: ").lower()
	
	while player_two not in allowed_entries:
		print "ERROR: Wrong Entry " + player_one
		player_two = raw_input("Player Two - enter rock, paper or scissors: ").lower()
		
	if player_one == player_two:
		print "Player One and Player Two are tied"
	elif player_one == "paper" and player_two == "scissors":
		print "Player Two Wins"
	elif player_one == "paper" and player_two == "rock":
		print "Player One Wins"
	elif player_one == "rock" and player_two == "paper":
		print "Player Two Wins"
	elif player_one == "rock" and player_two == "scissors":
		print "Player One Wins"
	elif player_one == "scissors" and player_two == "rock":
		print "Player Two Wins"
	elif player_one == "scissors" and player_two == "paper":
		print "Player One Wins"
	else:
		print "Unknown Winner"
	
	play_again = raw_input("Do you want to play again [Yes|No]: ")
	if play_again in ['Yes', 'YES', 'Y', 'y', 'yes']:
		print "Continue Play"
	elif play_again in ['No', 'NO', 'N', 'n', 'no']:
		print "Play Ends"
		break
	else:
		print "Unknown Answer, Play Ends"
		break
		
exit (0)
