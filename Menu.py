from random import randrange
from time import sleep, time
from decimal import Decimal

from Game_Engine import Game
from Enemy import Enemy
from Equipment import Item
from Generate_objects_indexes import GenerateMisc, GenerateWolf, GeneratePotato
from Character import StartingChoices


class GameMain:
    def __init__(self):

        self.game_now = Game()
        self.save = 0
        self.load = 0
        self.end = 0
        self.dead = 0
        self.x = 0

        # How many times you talked with NPC
        self.meet_mals = {"Alchemist": [0, 0], "Guard": [0, 0], "Monk": [0, 0]}

        # GENERATE ITEMS ON THE GROUND
        self.items_map = []
        for i in range(100):
            self.items_map.append([])

        self.items_spawn = GenerateMisc(
            self.game_now.now_map.river_location, self.game_now.now_map.mountain_location,
            self.game_now.now_map.city_location, self.game_now.now_map.village_location,
            self.game_now.now_map.sea_location)
        self.misc_and_indexes = {"0": ["R", "Reed"], "1": ["P", "Potato"]}

        # SPAWN ITEMS
        for i in range(100):
            for k in range(len(self.misc_and_indexes) - 1):
                if i in self.items_spawn.misc[k]:
                    self.items_map[i].append(Item(self.misc_and_indexes[str(k)][1]))

        # FREE X FOR WOLF
        self.occupied_x = []
        for i in range(len(self.items_spawn.misc)):
            for k in range(len(self.items_spawn.misc[i])):
                self.occupied_x.append(self.items_spawn.misc[i][k])
        for i in range(len(self.game_now.enemies_spawn.enemies)):
            for k in range(len(self.game_now.enemies_spawn.enemies[i])):
                self.occupied_x.append(self.game_now.enemies_spawn.enemies[i][k])
        for i in range(100):
            if self.game_now.now_map.map[i] != "O":
                self.occupied_x.append(i)
        self.free_x = []
        for i in range(100):
            if i not in self.occupied_x:
                self.free_x.append(i)

        # Do not spawn wolf in range of 1st move
        if self.game_now.x + 1 in self.free_x:
            self.free_x.remove(self.game_now.x + 1)
        if self.game_now.x - 1 in self.free_x:
            self.free_x.remove(self.game_now.x - 1)
        if self.game_now.x == 25:
            self.free_x.remove(15)
        if self.game_now.x == 75:
            self.free_x.remove(85)
        # GENERATE WOLF
        self.wolf_spawn = GenerateWolf()
        self.free_x_potato = self.wolf_spawn.wolf_x(self.free_x)
        # SPAWN WOLF
        self.game_now.enemies_spawn.enemies.append(self.wolf_spawn.wolf)
        for i in range(100):
            if i in self.game_now.enemies_spawn.enemies[4]:
                self.game_now.now_map.map[i] = "w"

        # GENERATE POTATO
        self.potato_spawn = GeneratePotato()
        self.potato_spawn.potato_x(self.free_x_potato)
        self.items_spawn.misc.append(self.potato_spawn.potato)
        # SPAWN POTATO
        for i in range(100):
            if i in self.items_spawn.misc[1]:
                self.items_map[i].append(Item(self.misc_and_indexes[str(1)][1]))

        # ----------------------------------------------------------
        # GAME
        # ----------------------------------------------------------

        # FIRST MOVE
        self.game_now.now_map.print_map(if_got_map=0)
        print("_" * 50)
        StartingChoices.first_move(self)
        user_input = 0
        while user_input not in ["w", "s", "a", "d"]:
            user_input = Checking.check_input_move(self)
        x = self.game_now.choose_direction(self.game_now.x, user_input)

        # SECOND MOVE
        self.game_now.now_map.print_map(if_got_map=0)
        print("_" * 50)
        StartingChoices.insist_show_help(self)
        self.help()
        StartingChoices.second_move(self)
        self.automatic_loop(x)

    def automatic_loop(self, x):
        user_input = 0
        while True:
            while user_input not in ["w", "s", "a", "d"]:
                user_input = GameMain.non_automatic_loop(self, x)
                if user_input == "save":
                    self.save = 1
                    break
                if user_input == "load":
                    self.load = 1
                    break
                if user_input == "end":
                    self.end = 1
                    break
            if self.save == 1:
                self.x = x
                break
            if self.load == 1:
                self.game_now.now_map.map[x] = "O"
                break
            if self.end == 1:
                break
            print("")
            x = self.game_now.choose_direction(x, user_input)

            self.show_map()

            # ----------------------------------------------------------
            # AUTOMATIC ->> THESE MUST BE CHECKED AFTER EVERY MOVE
            # ----------------------------------------------------------

            # Run fight mode if possible
            if self.game_now.check_if_able_to_fight(x, self.game_now.enemies_spawn.enemies):
                GameMain.battle(self, x)
            if self.dead == 1:
                decision = 0
                while decision not in ["load", "end"]:
                    decision = input("Type 'load' to try again or type 'end' to exit game")
                if decision == "end":
                    self.end = 1
                    break
                else:
                    self.load = 1
                    break

            if len(self.game_now.enemies_spawn.enemies[3]) == 0:
                for i in range(10):
                    sleep(0.5)
                    print("*" * (10 - i))
                print("Congratulations.")
                print("You have won.")
                for i in range(10):
                    sleep(0.5)
                    print("*" * i)
                print("Natoo 2017.")
                self.end = 1
                break

            # Display items on the ground
            try:
                if self.items_map[x][0] != 0:
                    self.display_items_on_the_ground(x)
            except IndexError:
                pass

            # Display NPC you met
            if x in self.game_now.NPC_spawn.NPC:
                self.display_NPC_you_met(x)

            # Check whether player can open the gate
            if "Golden Key" in self.game_now.player.Eq1.items_names() and x == self.game_now.now_map.camp_gate + 1:
                self.open_gate(x)

            # ----------------------------------------------------------
            # NON-AUTOMATIC ->> PLAYER CAN CHOOSE
            # ----------------------------------------------------------
            user_input = GameMain.non_automatic_loop(self, x)
            if user_input == "save":
                self.save = 1
            if user_input == "load":
                self.load = 1
            if user_input == "end":
                self.end = 1
                break
            if self.save == 1:
                self.x = x
                break
            if self.load == 1:
                self.game_now.now_map.map[x] = "O"
                break
            if self.end == 1:
                break

    def non_automatic_loop(self, x):
        user_input = 0
        while user_input not in ["w", "s", "a", "d"]:
            user_input = Checking.check_input_other(self)

            # Main Menu
            if user_input == "0":
                main_choice = 1
                while main_choice not in ["save", "load", "0", "end"]:
                    main_choice = input("Type save or load (or 0 to go back), (or end to exit game): ")
                    if main_choice == "save":
                        user_input = "save"
                    if main_choice == "load":
                        user_input = "load"
                    if main_choice == "end":
                        user_input = "end"
                break

            # Move if input == wasd
            if user_input in ["w", "s", "a", "d"]:
                break

            # DISPLAY HELP/KEYBOARD POSSIBILITIES
            if user_input == "h":
                self.help()

            # Talk with NPC
            if user_input == "n":
                if x in self.game_now.NPC_spawn.NPC:
                    self.talk(x)
                else:
                    print("There is no one here you can talk with")

            # Trade with NPC
            if user_input == "t":
                if x in self.game_now.NPC_spawn.NPC:
                    self.trade(x)
                else:
                    print("There is no one here you can trade with")

            # Collect items from the ground
            if user_input == "c":
                if len(self.items_map[x]) != 0:
                    self.collect_items(x)
                else:
                    print("There is nothing here you can take.")

            # Change weapon
            if user_input == "q":
                self.change_weapon()

            # Drink or eat
            if user_input == "e":
                self.eat_drink()

            # Display equipment
            if user_input == "i":
                self.game_now.player.Eq1.display_eq()

            # Display map
            if user_input == "m":
                self.show_map()

            # Display stats
            if user_input == "b":
                self.display_stats()
        return user_input

    def open_gate(self, x):
        print("1. Open the gate.")
        print("0. Don't do anything.")
        final_decision = 0
        while final_decision not in ["0", "1"]:
            final_decision = input("Type the number: ")
        if final_decision == "0":
            return
        else:
            print("-" * 50)
            print("Golden Key has been removed from your inventory.")
            print("-" * 50)
            for i in range(len(self.game_now.player.Eq1.elements)):
                if self.game_now.player.Eq1.elements[i].name == "Golden Key":
                    self.game_now.player.Eq1.remove_element(i)
                    break
            self.game_now.now_map.map[self.game_now.now_map.camp_gate] = "O"



    def change_weapon(self):
        self.game_now.player.Eq1.display_weapons()
        weapons_list = ["0"]
        for i in range(len(self.game_now.player.Eq1.elements)):
            if self.game_now.player.Eq1.elements[i].is_weapon in [1,2]:
                weapons_list.append(self.game_now.player.Eq1.elements[i].name)
        weapon_name = 0
        while weapon_name not in weapons_list:
            weapon_name = input("Which weapon do you want to use? Type the name: (type 0 to go back)")
        if weapon_name == "0":
            return
        for i in range(len(self.game_now.player.Eq1.elements)):
            if self.game_now.player.Eq1.elements[i].is_weapon == 2:
                self.game_now.player.Eq1.elements[i].is_weapon = 1
        for i in range(len(self.game_now.player.Eq1.elements)):
            if self.game_now.player.Eq1.elements[i].name == weapon_name:
                self.game_now.player.Eq1.elements[i].is_weapon = 2
                print("-" * 50)
                print(weapon_name, "is now being used.")
                print("-" * 50)
                return

    def eat_drink(self):
        possible_to_consume = ["0"]
        item_name = 0
        self.game_now.player.Eq1.display_items_eat_drink()
        for i in range(len(self.game_now.player.Eq1.elements)):
            if self.game_now.player.Eq1.elements[i].points != None:
                possible_to_consume.append(self.game_now.player.Eq1.elements[i].name)
        while item_name not in possible_to_consume:
            item_name = input("What do you want to consume? Type the name (type 0 to go back)")
        if item_name == "0":
            return
        # for i in range(len(possible_to_consume)):
        #     if number == possible_to_consume[i]:
        #         this = i
        # a = int(possible_to_consume[this - 1])
        # item_name = self.game_now.player.Eq1.elements[a].name
        for i in range(len(self.game_now.player.Eq1.elements)):
            if item_name in ["Potato", "Bottle of Water"]:
                if self.game_now.player.Eq1.elements[i].name == item_name:
                    hp_start = self.game_now.player.hp
                    hp = self.game_now.player.hp + self.game_now.player.Eq1.elements[i].points
                    if hp > self.game_now.player.hp_max:
                        self.game_now.player.hp = self.game_now.player.hp_max
                    else:
                        self.game_now.player.hp = hp
                    hp_gain = self.game_now.player.hp - hp_start
                    print("You restored", hp_gain, "HP.")
                    self.game_now.player.Eq1.remove_element(i)
                    return
            if item_name == "HP Potion":
                if self.game_now.player.Eq1.elements[i].name == item_name:
                    self.game_now.player.hp_max += self.game_now.player.Eq1.elements[i].points
                    self.game_now.player.hp = self.game_now.player.hp_max
                    print("Your HP has been increased by", self.game_now.player.Eq1.elements[i].points)
                    self.game_now.player.Eq1.remove_element(i)
                    return
            if item_name == "Strength Potion":
                if self.game_now.player.Eq1.elements[i].name == item_name:
                    self.game_now.player.strength += self.game_now.player.Eq1.elements[i].points
                    print("Your strength has been increased by", self.game_now.player.Eq1.elements[i].points)
                    self.game_now.player.Eq1.remove_element(i)
                    return
            if item_name == "Agility Potion":
                if self.game_now.player.Eq1.elements[i].name == item_name:
                    self.game_now.player.agility += self.game_now.player.Eq1.elements[i].points
                    print("Your agility has been increased by", self.game_now.player.Eq1.elements[i].points)
                    self.game_now.player.Eq1.remove_element(i)
                    return

    def choose_NPC(self, x):
        for i in range(len(self.game_now.NPC_spawn.NPC)):
            if x == self.game_now.NPC_spawn.NPC[i]:
                if i == 0:
                    NPC = self.game_now.alchemist
                if i == 1:
                    NPC = self.game_now.blacksmith
                if i == 2:
                    NPC = self.game_now.cartographer
                if i == 3:
                    NPC = self.game_now.innkeeper_city
                if i == 4:
                    NPC = self.game_now.innkeeper_village
                if i == 5:
                    NPC = self.game_now.merchant_city
                if i == 6:
                    NPC = self.game_now.merchant_village
                if i == 7:
                    NPC = self.game_now.guard
                if i == 8:
                    NPC = self.game_now.monk
        return NPC

    def talk(self, x):
        NPC = self.choose_NPC(x)
        i = 0
        good = 0
        if NPC.name == "Alchemist":
            if self.meet_mals[NPC.name][1] == 0:
                self.talk_alchemist(i, good, NPC)
                self.meet_mals[NPC.name][1] = 1
                return
            if self.meet_mals[NPC.name][0] == 0:
                self.meet_mals[NPC.name][0] = 1
                self.talk_alchemist(i, good, NPC)
                return
            if self.meet_mals[NPC.name][0] == 1:
                self.quest_alchemist()
                self.talk_alchemist(i, good, NPC)
                return
            if self.meet_mals[NPC.name][0] == 2:
                self.meet_mals[NPC.name][0] = 3
                self.talk_alchemist(i, good, NPC)
                self.meet_mals[NPC.name][0] = 2
                return
        if NPC.name == "Blacksmith":
            self.talk_blacksmith(NPC)
        if NPC.name == "Cartographer":
            self.talk_cartographer(NPC)
        if NPC.name == "Innkeeper":
            self.talk_innkeeper(NPC)
        if NPC.name == "Merchant":
            self.talk_merchant(NPC)
        if NPC.name == "Guard":
            if self.meet_mals[NPC.name][1] == 0:
                self.talk_guard(i, good, NPC)
                self.meet_mals[NPC.name][1] = 1
                return
            if self.meet_mals[NPC.name][0] == 0:
                self.meet_mals[NPC.name][0] = 1
                self.talk_guard(i, good, NPC)
                return
            if self.meet_mals[NPC.name][0] == 1:
                self.quest_guard()
                self.talk_guard(i, good, NPC)
                return
            if self.meet_mals[NPC.name][0] == 2:
                self.meet_mals[NPC.name][0] = 3
                self.talk_guard(i, good, NPC)
                self.meet_mals[NPC.name][0] = 2
                return
        if NPC.name == "Monk":
            if self.meet_mals[NPC.name][1] == 0:
                self.talk_monk(i, good, NPC)
                self.meet_mals[NPC.name][1] = 1
                return
            if self.meet_mals[NPC.name][0] == 0:
                self.meet_mals[NPC.name][0] = 1
                self.talk_monk(i, good, NPC)
                return
            if self.meet_mals[NPC.name][0] == 1:
                self.quest_monk()
                self.talk_monk(i, good, NPC)
                return
            if self.meet_mals[NPC.name][0] == 2:
                self.meet_mals[NPC.name][0] = 3
                self.talk_monk(i, good, NPC)
                self.meet_mals[NPC.name][0] = 2
                return

    def talk_monk(self, i, good, NPC):
        while good != 1:
            if self.game_now.monk.dialogues[i] == self.meet_mals["Monk"][0]:
                good = 1
                k = self.meet_mals[NPC.name][0] + 1
            i += 1
        print(">" * 30)
        while self.game_now.monk.dialogues[i] != k:
            print(NPC.name, end="")
            print(": ", end="")
            if k == 2:
                if i == 10:
                    sleep(0.8)
            print(self.game_now.monk.dialogues[i])
            sleep(0.8)
            i += 1
        print("<" * 30)

    def quest_monk(self):
        if "Bone Sword" in self.game_now.player.Eq1.items_names() and self.game_now.monk.quest == 0:
            self.game_now.monk.quest = 1
            for i in range(len(self.game_now.player.Eq1.elements)):
                if self.game_now.player.Eq1.elements[i].name == "Bone Sword":
                    self.game_now.player.Eq1.remove_element(i)
                    break
            self.meet_mals["Monk"][0] = 2
            self.game_now.player.Eq1.add_element("Golden Key")
            print("-" * 50)
            print("Silver Claymore has been been removed from your inventory.")
            print("-" * 50)
            print("-" * 50)
            print("Golden key has been been added to your inventory.")
            print("-" * 50)

    def talk_merchant(self, NPC):
        i = 1
        print("")
        print(">" * 30)
        while self.game_now.merchant_city.dialogues[i] != 1:
            print(NPC.name, end="")
            print(": ", end="")
            sleep(0.8)
            print(self.game_now.merchant_city.dialogues[i])
            i += 1
        sleep(0.8)
        print("<" * 30)

    def talk_cartographer(self, NPC):
        i = 1
        print("")
        print(">" * 30)
        while self.game_now.cartographer.dialogues[i] != 1:
            print(NPC.name, end="")
            print(": ", end="")
            sleep(0.8)
            print(self.game_now.cartographer.dialogues[i])
            i += 1
        sleep(0.8)
        print("<" * 30)

    def talk_guard(self, i, good, NPC):
        while good != 1:
            if self.game_now.guard.dialogues[i] == self.meet_mals["Guard"][0]:
                good = 1
                k = self.meet_mals[NPC.name][0] + 1
            i += 1
        print(">" * 30)
        while self.game_now.guard.dialogues[i] != k:
            print(NPC.name, end="")
            print(": ", end="")
            if k == 2:
                if i == 10:
                    sleep(0.8)
            print(self.game_now.guard.dialogues[i])
            sleep(0.8)
            i += 1
        print("<" * 30)

    def quest_guard(self):
        if len(self.game_now.enemies_spawn.enemies[0]) == 0 and self.game_now.guard.quest == 0:
            self.game_now.guard.quest = 1
            self.game_now.player.Eq1.add_element("Silver Claymore")
            self.meet_mals["Guard"][0] = 2
            print("-" * 50)
            print("Silver Claymore has been added to your inventory.")
            print("-" * 50)

    def talk_alchemist(self, i, good, NPC):
        while good != 1:
            if self.game_now.alchemist.dialogues[i] == self.meet_mals["Alchemist"][0]:
                good = 1
                k = self.meet_mals[NPC.name][0] + 1
            i += 1
        print(">" * 30)
        while self.game_now.alchemist.dialogues[i] != k:
            print(NPC.name, end="")
            print(": ", end="")
            if k == 2:
                if i == 10:
                    sleep(1)
            print(self.game_now.alchemist.dialogues[i])
            sleep(0.8)
            i += 1
        print("<" * 30)

    def quest_alchemist(self):
        k = 0
        for i in range(len(self.game_now.player.Eq1.elements)):
            if self.game_now.player.Eq1.elements[i].name == "Reed":
                k += 1
        if k > 4 and self.game_now.alchemist.quest == 0:
            reed = 0
            self.game_now.alchemist.quest = 1
            i = 0
            while reed < 5:
                if self.game_now.player.Eq1.elements[i].name == "Reed":
                    self.game_now.player.Eq1.remove_element(i)
                    reed += 1
                    i = 0
                i += 1
            self.meet_mals["Alchemist"][0] = 2
            self.game_now.player.Eq1.add_element("HP Potion")
            print("-" * 50)
            print("HP Potion has been added to your inventory.")
            print("-" * 50)

    def talk_blacksmith(self, NPC):
        i = 1
        print("")
        print(">" * 30)
        while self.game_now.blacksmith.dialogues[i] != 1:
            print(NPC.name, end="")
            print(": ", end="")
            sleep(0.8)
            print(self.game_now.blacksmith.dialogues[i])
            i += 1
        sleep(0.8)
        print("<" * 30)

    def talk_innkeeper(self, NPC):
        i = 1
        print("")
        print(">" * 30)
        while self.game_now.innkeeper_city.dialogues[i] != 1:
            print(NPC.name, end="")
            print(": ", end="")
            sleep(0.8)
            print(self.game_now.innkeeper_city.dialogues[i])
            i += 1
        user_choice = 3
        print("<" * 30)
        print("")
        print("1. Take a bed for a night for 20 gold.")
        print("0. Exit inn.")
        while user_choice not in ["1", "0"]:
            user_choice = input("Type the number: ")
        user_choice = int(user_choice)
        if user_choice == 0:
            return
        if user_choice == 1:
            self.game_now.player.Eq1.gold -= 20
            print("-" * 50)
            print("20 gold has been removed from your inventory.")
            print("-" * 50)
            print("-" * 50)
            print("Health points: ", self.game_now.player.hp, "/", self.game_now.player.hp_max)
            print("-" * 50)
            sleep(1.5)
            for i in range(10):
                print("Z" * (10 - i))
                sleep(0.5)
            self.game_now.player.hp = self.game_now.player.hp_max
            print("-" * 50)
            print("Health points: ", self.game_now.player.hp, "/", self.game_now.player.hp_max)
            print("-" * 50)

    def show_map(self):
        if "Map" in self.game_now.player.Eq1.items_names():
            self.game_now.now_map.print_map(if_got_map=1)
        else:
            self.game_now.now_map.print_map(if_got_map=0)

    def display_eq_trade_trader(self, trader):
        print("*" * 50)
        print("EQUIPMENT OF", trader.name.upper(), "             ",
              "GOLD:", trader.Equipment.gold)
        print("*" * 50)
        trader.Equipment.display_eq()
        print("Your gold:", self.game_now.player.Eq1.gold)
        print("")

    def display_eq_trade_player(self):
        print("*" * 50)
        print("YOUR EQUIPMENT", "                       ", "GOLD:", self.game_now.player.Eq1.gold)
        print("*" * 50)
        self.game_now.player.Eq1.display_eq()
        print("")

    def trade(self, x):
        no_sell = 0
        trader = self.choose_NPC(x)
        user_choice = None
        while user_choice != "0":
            while user_choice not in ["1", "2", "0"]:
                if no_sell == 0:
                    self.display_eq_trade_player()
                    self.display_eq_trade_trader(trader)
                    no_sell = 0
                print("")
                print("Do you want to buy or sell something?")
                print("1. Buy.")
                print("2. Sell")
                print("0. End trading")
                user_choice = input("Type the number: ")
                print("")
                end = None
                if user_choice == "1":
                    while end != "0":
                        self.display_eq_trade_trader(trader)
                        end = self.buying_mode(trader)
                if user_choice == "2":
                    if trader.name in ["Merchant"]:
                        while end != "0":
                            self.display_eq_trade_player()
                            end = self.selling_mode(trader)
                    else:
                        print(trader.name, "does not buy anything.")
                        no_sell = 1
                if user_choice == "0":
                    break
            if user_choice != "0":
                user_choice = None

    def give_names_buy(self, trader):
        names = []
        for i in range(len(trader.Equipment.elements)):
            names.append(trader.Equipment.elements[i].name)
        return names

    def give_names_sell(self):
        names = []
        for i in range(len(self.game_now.player.Eq1.elements)):
            names.append(self.game_now.player.Eq1.elements[i].name)
        return names

    def buying_mode(self, trader):
        names = self.give_names_buy(trader)
        name = 1
        print("What would you like to buy?")
        names.append("0")
        while name not in names:
            name = input("Type the item's name (or type 0 to end buying):")
            if name == "0":
                return name
            if name == "Golden Key":
                print(trader.name, "does not sell this item.")
                break
            for i in range(len(trader.Equipment.elements)):
                if name == trader.Equipment.elements[i].name:
                    if self.game_now.player.Eq1.gold >= trader.Equipment.elements[i].value:
                        print("")
                        print("-" * 50)
                        print("You bought", name, "for", trader.Equipment.elements[i].value, "gold.")
                        print("-" * 50)
                        self.game_now.player.Eq1.gold -= trader.Equipment.elements[i].value
                        trader.Equipment.gold += trader.Equipment.elements[i].value
                        self.game_now.player.Eq1.add_element(name)
                        trader.Equipment.remove_element(i)
                        break
                    else:
                        print("You do not have enough gold.")
                        name = 1
                if i == len(trader.Equipment.elements):
                    print(trader.name, "do not sell this item")

    def selling_mode(self, trader):
        names = self.give_names_sell()
        name = 1
        print("What would you like to sell?")
        names.append("0")
        while name not in names:
            name = input("Type the item's name (or type 0 to end selling):")
            if name == "0":
                return name
            if name == "Golden Key":
                print("You cannot sell this item.")
                continue
            for i in range(len(self.game_now.player.Eq1.elements)):
                if name == self.game_now.player.Eq1.elements[i].name:
                    if trader.Equipment.gold >= self.game_now.player.Eq1.elements[i].value:
                        print("")
                        print("-" * 50)
                        print("You sold", name, "for", self.game_now.player.Eq1.elements[i].value, "gold.")
                        print("-" * 50)
                        self.game_now.player.Eq1.gold += self.game_now.player.Eq1.elements[i].value
                        trader.Equipment.gold -= self.game_now.player.Eq1.elements[i].value
                        trader.Equipment.add_element(name)
                        self.game_now.player.Eq1.remove_element(i)
                        break
                    else:
                        print(trader.name, " do not have enough gold.")
                if i == len(self.game_now.player.Eq1.elements):
                    print("You do not have this item.")

    def display_NPC_you_met(self, x):
        for i in range(len(self.game_now.NPC_and_indexes)):
            if x == self.game_now.NPC_spawn.NPC[i]:
                NPC_here = i
        print("There is", self.game_now.NPC_and_indexes[str(NPC_here)], "here. You can talk with him.")

    def help(self):
        print("")
        print("Keyboard options:")
        print("0 - Main Menu")
        print("w - go north")
        print("s - go south")
        print("a - go west")
        print("d - go east")
        print("b - display player's stats")
        print("c - collect items from the ground")
        print("e - eat or drink")
        print("i - display your equipment")
        print("m - display map")
        print("n - talk with NPC")
        print("q - change weapon")
        print("t - trade with NPC")
        print("")

    def display_items_on_the_ground(self, x):
        print("-" * 50)
        print("You can see", end=" ")
        for i in range(len(self.items_map[x])):
            if i + 1 == len(self.items_map[x]):
                print(self.items_map[x][i].name, end=" ")
            else:
                print(self.items_map[x][i].name, end=", ")
        print("on the ground.")
        print("-" * 50)


    def collect_items(self, x):
        quantity = len(self.items_map[x])
        if quantity == 1:
            self.game_now.player.Eq1.add_element(self.items_map[x][0].name)
            print(self.items_map[x][0].name, end=" ")
            self.items_map[x].remove(self.items_map[x][0])
            print("has been added to your inventory.")
        else:
            while True:
                for i in range(quantity):
                    self.game_now.player.Eq1.add_element(self.items_map[x][i].name)
                print("Items have been added to your inventory")
                try:
                    n = 0
                    for i in range(quantity):
                        self.items_map[x].remove(self.items_map[x][i - n])
                        n += 1
                except IndexError:
                    pass
                break


    def display_stats(self):
        print("-" * 50)
        print("Health points: ", self.game_now.player.hp, "/", self.game_now.player.hp_max)
        print("Strength: ", self.game_now.player.strength)
        print("Agility: ", self.game_now.player.agility)
        print("-" * 50)

    def choose_opponent(self, x):
        for i in range(len(self.game_now.enemies_spawn.enemies)):
            if x in self.game_now.enemies_spawn.enemies[i]:
                enemy_name = self.game_now.enemies_and_indexes[str(i)][1]
        return enemy_name

    def battle(self, x):
        # Player statistics
        weapon_index = 0
        if_fists = 0
        for i in range(len(self.game_now.player.Eq1.elements)):
            if self.game_now.player.Eq1.elements[i].is_weapon == 2:
                weapon_index = i
        try:
            player_dmg = self.game_now.player.strength * self.game_now.player.Eq1.elements[weapon_index].damage
            player_as = self.game_now.player.agility * self.game_now.player.Eq1.elements[weapon_index].attack_speed
        # IF PLAYER HAS NO WEAPON
        except TypeError:
            player_dmg = self.game_now.player.strength * 5
            player_as = self.game_now.player.agility * 5
            if_fists = 1
        player_hp = self.game_now.player.hp

        # Enemy statistics
        enemy_name = GameMain.choose_opponent(self, x)
        enemy = Enemy(enemy_name)
        weapon_index = 0
        max_dmg = 0
        for i in range(len(enemy.Equipment.elements)):
            if enemy.Equipment.elements[i].is_weapon == 1 or enemy.Equipment.elements[i].is_weapon == 2:
                if enemy.Equipment.elements[i].damage > max_dmg:
                    weapon_index = i
                    max_dmg = enemy.Equipment.elements[i].damage
        enemy_dmg = enemy.strength * enemy.Equipment.elements[weapon_index].damage
        enemy_as = enemy.agility * enemy.Equipment.elements[weapon_index].attack_speed
        enemy_hp = enemy.hp

        player_as = round((1 / player_as) * 1000)
        enemy_as = round((1 / enemy_as) * 1000)
        player_time_begin = time()
        enemy_time_begin = time()
        print("+" * 50)
        print("BATTLE HAS STARTED")
        print("YOU ARE FIGHTING AGAINST", enemy_name.upper())
        if if_fists == 1:
            print("YOU ARE FIGHTING WITH YOR FISTS!")
        print("+" * 50)
        while player_hp > 0 and enemy_hp > 0:
            sleep(0.1)
            player_time_now = time()
            enemy_time_now = time()
            enemy_dmg_now = round(enemy_dmg * randrange(75, 126) / 100)
            player_dmg_now = round(player_dmg * randrange(75, 126) / 100)
            player_time_check = int(Decimal(player_time_now - player_time_begin) * 10)
            enemy_time_check = int(Decimal(enemy_time_now - enemy_time_begin) * 10)

         #   print(player_time_check)
        #    print("       ", enemy_time_check)

            # Player's hit
            if player_time_check == player_as:
                enemy_hp = enemy_hp - player_dmg_now
                if enemy_hp > 0:
                    print("You dealt", player_dmg_now, "damage.", enemy_name, "has", enemy_hp, "left.")
                else:
                    self.game_now.player.hp = player_hp
                    # Player killed an enemy
                    print("You dealt ", player_dmg_now, "damage. ")
                    print("+" * 50)
                    print(enemy_name.upper(), "HAS BEEN SLAIN.")
                    print("+" * 50)
                    # Drop items on the ground
                    n = 0
                    for i in range(len(enemy.Equipment.elements)):
                        if n == 0:
                            if enemy.Equipment.elements[i].name in ["Teeth", "Paw"]:
                                enemy.Equipment.elements.pop(i)
                                n = 1
                    for i in range(len(enemy.Equipment.elements)):
                        self.items_map[x].append(Item(enemy.Equipment.elements[i].name))
                    # Delete enemy from this coord
                    for i in range(len(self.game_now.enemies_spawn.enemies)):
                        if x in self.game_now.enemies_spawn.enemies[i]:
                            self.game_now.enemies_spawn.enemies[i].remove(x)
                    break
                player_time_begin = time()

            # Enemy's hit
            if enemy_time_check == enemy_as:
                player_hp = player_hp - enemy_dmg_now
                if player_hp > 0:
                    print(enemy_name, "dealt", enemy_dmg_now, "damage. You have", player_hp, "left.")
                else:
                    # Player dies
                    print(enemy_name, " dealt ", enemy_dmg_now, "damage.")
                    print("+" * 50)
                    print("You are dead.")
                    print("+" * 50)
                    self.dead = 1
                    break
                enemy_time_begin = time()


class Checking:
    def check_input_move(self):
        user_input = 0
        while user_input not in ["w", "a", "s", "d"]:
            print("_" * 50)
            user_input = input("Type the sign: ")
        return user_input

    def check_input_other(self):
        user_input = 0
        while user_input not in ["w", "a", "s", "d", "c", "i", "m", "h", "b", "t", "n", "e", "q", "0"]:
            print("___________________________________________________________________________")
            user_input = input("What do you want to do? (type h for help) ")
        return user_input