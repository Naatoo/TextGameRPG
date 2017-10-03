from Menu import GameMain
from copy import deepcopy
from time import sleep

game = GameMain()

saves = []
saves_names = []
while True:
    if game.end == 1:
        print("-" * 50)
        sleep(1)
        print("Thank you for playing.")
        sleep(1)
        print("Natoo 2017")
        sleep(1)
        print("-" * 50)
        break
    if game.save == 1:
        game.save = 0
        name = input("give save's name: ")
        saves_names.append(name)
        saves.append(deepcopy(game))
        game.save = 0
        game.automatic_loop(game.x)
    if game.load == 1:
        if len(saves) == 0:
            print("You have no saves, try again.")
            break
        game.load = 0
        for i in range(len(saves_names)):
            print(saves_names[i])
        name = None
        while name not in saves_names:
            name = input("Type the save's name: ")
        for i in range(len(saves_names)):
            if name == saves_names[i]:
                game = saves[i]
        game.load = 0
        game.automatic_loop(game.x)


