import numpy as np
import tabulate

BASE_STATS = {
    1: {
        0: [10, 0, 5, 0, 0, 2, -21],   # Speed: [speed, stamina, power, guts, intelligence, sp, ???, energy_cost]
        1: [0, 9, 0, 4, 0, 2, -19],    # Stamina
        2: [0, 5, 8, 0, 0, 2, -20],    # Power
        3: [4, 0, 4, 8, 0, 2, -22],    # Guts
        4: [2, 0, 0, 0, 9, 4, 5],      # Intelligence
    },
    2: {
        0: [11, 0, 5, 0, 0, 2, -22],
        1: [0, 10, 0, 4, 0, 2, -20],
        2: [0, 5, 9, 0, 0, 2, -21],
        3: [4, 0, 4, 9, 0, 2, -23],
        4: [2, 0, 0, 0, 10, 4, 5],
    },
    3: {
        0: [12, 0, 5, 0, 0, 2, -23],
        1: [0, 11, 0, 4, 0, 2, -21],
        2: [0, 5, 10, 0, 0, 2, -22],
        3: [4, 0, 4, 10, 0, 2, -24],
        4: [2, 0, 0, 0, 11, 4, 5],
    },
    4: {
        0: [13, 0, 6, 0, 0, 2, -25],
        1: [0, 12, 0, 5, 0, 2, -23],
        2: [0, 6, 11, 0, 0, 2, -24],
        3: [5, 0, 4, 11, 0, 2, -26],
        4: [3, 0, 0, 0, 12, 4, 5],
    },
    5: {
        0: [14, 0, 7, 0, 0, 2, -27],
        1: [0, 13, 0, 6, 0, 2, -25],
        2: [0, 7, 12, 0, 0, 2, -26],
        3: [5, 0, 5, 12, 0, 2, -28],
        4: [4, 0, 0, 0, 13, 4, 5],
    },
}

FACILITY_MAP = {
    0: 'Speed',
    1: 'Stamina',
    2: 'Power',
    3: 'Guts',
    4: 'Wit',
}

MOOD_MAP = {
    0: 'Awful',
    1: 'Bad',
    2: 'Normal',
    3: 'Good',
    4: 'Great'
}


class uma():
    def __init__(self, energy=100, stats=[50, 50, 50, 50, 50, 0], growth_rate=[1, 1, 1, 1, 1, 1], mood=2, fans=1, debug=False):
        self.energy = energy
        self.stats = np.array(stats)  # [speed, stamina, power, guts, intelligence, sp]
        self.growth_rate = np.array(growth_rate)
        self.facility_clicks = np.array([0, 0, 0, 0, 0])
        self.mood = mood
        self.fans = fans
        self.turn = 1
        self.debug = debug

    # 0: speed, 1: stamina, 2: power, 3: guts, 4: wit, 5: sp
    def train(self, facility_i):
        facility_level = min((self.facility_clicks[facility_i] // 4) + 1, 5)

        support_flat_bonus = np.array([0, 0, 0, 0, 0, 0])
        base_values = np.array(BASE_STATS[facility_level][facility_i][:6])  # Extract first 6 values (stats)
        
        """ 
        Wiki formula: (base + ability_bonus) 
                        * growth_rate 
                        * (1 + mood_effect) 
                        * training_effect 
                        * (1 + 0.05 * support_count) 
                        * friendship_bonus 
        """
        mood_multiplier = 1 + (self.mood - 2) * 0.1
        training_modifier = 1
        n_supporters = 0
        friendship_bonus_modifier = 1
        
        total_training_stats = (base_values + support_flat_bonus) * \
                                self.growth_rate * \
                                mood_multiplier * \
                                training_modifier * \
                                (1 + 0.05 * n_supporters) * \
                                friendship_bonus_modifier

        training_stats_int = total_training_stats.astype(int)
        self.stats += training_stats_int

        energy_cost = abs(BASE_STATS[facility_level][facility_i][6])
        self.energy = max(0, self.energy - energy_cost)

        self.facility_clicks[facility_i] += 1
        self.turn += 1

        if self.debug:
            print(f'Training {FACILITY_MAP[facility_i]} Level {facility_level}: \n '
                  f'stat gains = {training_stats_int}')

    def recreate(self):
        recreate_names = {0: 'Shrine', 1: 'Park', 2: 'Karaoke'}
        recreate_type = np.random.randint(3) # 0: shrine, 1: park, 2: karaoke
        if recreate_type == 0:
            # TODO: remove all negative statuses
            self.energy += np.random.choice([10, 20, 30]) # double check this
            self.mood = min(self.mood + 1, 4)
        elif recreate_type == 1:
            self.energy += 10
            self.mood = min(self.mood + 1, 4)
        elif recreate_type == 2:
            self.mood = min(self.mood + 2, 4)

        if np.random.random() < 0.25:
            # implement later
            print('crane game')

        if self.debug:
            print(f'Recreated at {recreate_names[recreate_type]}, mood is now {MOOD_MAP[self.mood]}')

        self.turn += 1

    def get_stats(self):
        data = zip(FACILITY_MAP.values(), self.stats)
        return tabulate.tabulate(data, tablefmt='rounded_outline')