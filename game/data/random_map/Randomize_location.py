from random import choice


class GenerateEnemies:
    def __init__(self, river_location, mountain_location,
                 city_location, village_location, sea_location, camp_location):
        self.enemies = []
        self.enemies.append(GenerateEnemies.bandit(mountain_location))
        self.enemies.append(GenerateEnemies.skeleton(sea_location))
        self.enemies.append((GenerateEnemies.rat(city_location, village_location)))
        self.enemies.append((GenerateEnemies.giant(camp_location)))

    @staticmethod
    def bandit(mountain_location):
        bandit_location = []
        sign = 1
        if mountain_location == 9:
            sign = -1
        bandit_location.append((mountain_location + 1 * sign) * 10 + 6)
        for i in range(2):
            bandit_location.append((mountain_location + 2 * sign) * 10 + 7 + i)
        return bandit_location

    @staticmethod
    def skeleton(sea_location):
        skeleton_location = []
        sign = 1
        if sea_location[1] == 9:
            sign = -1
        skeleton_location.append(sea_location[1] * 10 + 3)
        for i in range(2):
            skeleton_location.append((sea_location[1] + 1 * sign) * 10 + 2 + i)
        return skeleton_location

    @staticmethod
    def rat(city_location, village_location):
        rat_location = []
        sign = 1
        for i in range(3):
            rat_location.append((city_location + i) * 10 + 7)
        if village_location in [3, 4]:
            sign = -1
        for i in range(3):
            rat_location.append((village_location + sign) * 10 + i)
        return rat_location

    @staticmethod
    def giant(camp_location):
        giant_location = []
        giant_location.append(camp_location * 10)
        return giant_location


class GenerateItemsGround:
    def __init__(self, river_location, mountain_location,
                 city_location, village_location, sea_location):
        self.misc = []
        self.misc.append((self.reed(river_location)))

    @staticmethod
    def reed(river_location):
        reed_location = []
        sign = 1
        if river_location == 5:
            sign = -1
        reed_location.append((river_location - 1 * sign) * 10 + 4)
        reed_location.append(river_location * 10 + 5)
        n = 0
        for i in range(2):
            reed_location.append((river_location + 1 * sign) * 10 + 3 + n)
            n += 3
        reed_location.append((river_location + 2 * sign) * 10 + 4)
        return reed_location


class GenerateNPC:
    def __init__(self, river_location, mountain_location,
                 city_location, village_location, sea_location):
        self.NPC = []

        # Random indexes for NPC in the city
        self.NPC_in_city = []
        for i in range(3):
            for k in range(2):
                self.NPC_in_city.append((city_location + i) * 10 + 8 + k)

        # Random indexes for NPC in the village
        self.NPC_in_village = []
        for i in range(3):
            self.NPC_in_village.append(village_location * 10 + i)

        # 6 NPC in the city, 3 NPC in village
        for NPCs_nr in range(6):
            self.x_NPC_city()
        for NPCs_nr in range(3):
            self.x_NPC_village()

    def x_NPC_city(self):
        NPC_choice_temp = choice(self.NPC_in_city)
        self.NPC.append(NPC_choice_temp)
        self.NPC_in_city.remove(NPC_choice_temp)

    def x_NPC_village(self):
        NPC_choice_temp = choice(self.NPC_in_village)
        self.NPC.append(NPC_choice_temp)
        self.NPC_in_village.remove(NPC_choice_temp)
