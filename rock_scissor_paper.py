import namegenerator as ng
from random import randint
import sys,os

class Game_namespace():
    def __init__(self,player1,player2):
        self.player1 = player1
        self.player2 = player2
    @property
    def get_player1(self):
        return self.player1
    @property
    def get_player2(self):
        return self.player2
    def print_choice(self):
        print("\t[1] Rock [2] Scissor [3] Paper")
    def gen_player2(self):
        return(str(randint(1,3)))
    @get_player1.setter
    def set_player1(self,player1_name):
        self.player1 = player1_name
    def check_result(self,player1_value,player2_value):
        variations1 = ["12", "31", "23"]
        variations2 = ["21", "13", "32"]
        tie = ["11", "22", "33"]
        value = str(player1_value) + str(player2_value)
        if value in variations1:
            return  "player1"
        if value in variations2:
            return "player2"
        if value in tie:
            return "tie"
    def print_value(self,number):
        if number == "1":
            return "Rock"
        elif number == "2":
            return "Scissor"
        elif number == "3":
            return "Paper"
    def play_again(self):
        q = input("\tDo you wanna try it again y/n?")
        if q == "y" or q == "":
            pass
        else:
            print("\tBye.")
            sys.exit(0)
os.system("clear")
wplayer1 = input("\tPlease enter your name or type 'exit' to leave the game: ")
if wplayer1 == "exit":
    sys.exit(1)
else:
    Game = Game_namespace(wplayer1,ng.gen())
    if wplayer1 == "":
        wplayer1 = ng.gen()
        Game.set_player1 = wplayer1
    print("\tHi " + Game.get_player1 + ".")
    print("\tI am " + Game.get_player2 + ".")
    print("\tLet's start.")
    while True:
        Game.print_choice()
        player1_value = input("\tEnter your choice or type 'exit' to give up: ")
        player2_value = Game.gen_player2()
        if player1_value == 'exit':
            print("\tCoward.")
            sys.exit(1)
        else:
            if player1_value not in ["1", "2", "3"]:
                print("\tWrong answer!Try it again.")
                pass
            else:
                if Game.check_result(player1_value, player2_value) == "player1":
                    print("\tYour hit " + Game.print_value(player1_value) + ", " +  Game.get_player2 + "'s hit " + Game.print_value(player2_value))
                    print("\t\x1b[6;30;42m Congratulation, you won! \x1b[0m")
                    Game.play_again()
                if Game.check_result(player1_value, player2_value) == "player2":
                    print("\tYour hit " + Game.print_value(player1_value) + ", " +  Game.get_player2 + "'s hit " + Game.print_value(player2_value))
                    print("\t\x1b[1;37;41m You lose, don't give up! \x1b[0m")
                    Game.play_again()
                if Game.check_result(player1_value, player2_value) == "tie":
                    print("\tYour hit " + Game.print_value(player1_value) + ", " +  Game.get_player2 + "'s hit " + Game.print_value(player2_value))
                    print("\t\x1b[1;37;43m It is a tie! \x1b[0m")
                    pass
            print("\t{:-<50}".format("-"))
