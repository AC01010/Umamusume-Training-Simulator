import numpy as np

BASE_STATS = {
    1: {
        0: [10, 0, 5, 0, 0, 0, 2, -21],   # Speed: [speed, stamina, power, guts, intelligence, sp, ???, energy_cost]
        1: [0, 9, 0, 4, 0, 0, 2, -19],    # Stamina
        2: [0, 5, 8, 0, 0, 0, 2, -20],    # Power
        3: [4, 0, 4, 8, 0, 0, 2, -22],    # Guts
        4: [2, 0, 0, 0, 9, 0, 4, 5],      # Intelligence
    },
    2: {
        0: [11, 0, 5, 0, 0, 0, 2, -22],
        1: [0, 10, 0, 4, 0, 0, 2, -20],
        2: [0, 5, 9, 0, 0, 0, 2, -21],
        3: [4, 0, 4, 9, 0, 0, 2, -23],
        4: [2, 0, 0, 0, 10, 0, 4, 5],
    },
    3: {
        0: [12, 0, 5, 0, 0, 0, 2, -23],
        1: [0, 11, 0, 4, 0, 0, 2, -21],
        2: [0, 5, 10, 0, 0, 0, 2, -22],
        3: [4, 0, 4, 10, 0, 0, 2, -24],
        4: [2, 0, 0, 0, 11, 0, 4, 5],
    },
    4: {
        0: [13, 0, 6, 0, 0, 0, 2, -25],
        1: [0, 12, 0, 5, 0, 0, 2, -23],
        2: [0, 6, 11, 0, 0, 0, 2, -24],
        3: [5, 0, 4, 11, 0, 0, 2, -26],
        4: [3, 0, 0, 0, 12, 0, 4, 5],
    },
    5: {
        0: [14, 0, 7, 0, 0, 0, 2, -27],
        1: [0, 13, 0, 6, 0, 0, 2, -25],
        2: [0, 7, 12, 0, 0, 0, 2, -26],
        3: [5, 0, 5, 12, 0, 0, 2, -28],
        4: [4, 0, 0, 0, 13, 0, 4, 5],
    },
}

FACILITY_MAP = {
    0: 'Speed',
    1: 'Stamina',
    2: 'Power',
    3: 'Guts',
    4: 'Wit',
}


class uma():
    def __init__(self, energy=100, stats=[50, 50, 50, 50, 50, 0], growth_rate=[1, 1, 1, 1, 1, 1], facility_clicks=[0, 0, 0, 0, 0], mood=2, fans=1, debug=False):
        self.energy = energy
        self.stats = np.array(stats)  # [speed, stamina, power, guts, intelligence, sp]
        self.growth_rate = np.array(growth_rate)
        self.facility_clicks = np.array(facility_clicks)
        self.mood = mood
        self.fans = fans
        self.turn = 0
        self.debug = debug

    # 0: speed, 1: stamina, 2: power, 3: guts, 4: wit, 5: sp
    def train(self, facility_i):
        facility_level = min((self.facility_clicks[facility_i] // 4) + 1, 5)
        support_flat_bonus = np.array([0, 0, 0, 0, 0, 0])
        base_values = np.array(BASE_STATS[facility_level][facility_i][:6])  # Extract first 6 values (stats)
        
        # Wiki formula: (base + ability_bonus) * growth_rate * (1 + mood_effect) * training_effect * (1 + 0.05 * support_count) * friendship_bonus
        motivation_effects = {0: -0.2, 1: -0.1, 2: 0, 3: 0.1, 4: 0.2}
        motivation_modifier = 1 + motivation_effects.get(self.mood, 0)
        training_modifier = 1
        n_supporters = 0  # number of support cards present
        friendship_bonus_modifier = 1
        
        total_training_stats = (base_values + support_flat_bonus) * \
                                self.growth_rate * \
                                motivation_modifier * \
                                training_modifier * \
                                (1 + 0.05 * n_supporters) * \
                                friendship_bonus_modifier

        # Apply stat gains (capped at reasonable values) - now includes SP as 6th stat
        self.stats += np.clip(total_training_stats, 0, 100)
        
        # Consume energy (energy cost is now at index 7)
        energy_cost = abs(BASE_STATS[facility_level][facility_i][7])
        self.energy = max(0, self.energy - energy_cost)
        
        # Track facility usage
        self.facility_clicks[facility_i] += 1
        self.turn += 1

        if self.debug:
            print(f'Training {FACILITY_MAP[facility_i]}')