import numpy as np

class support():
    def __init__(self, name, type, friendship_bonus, mood_effect, stat_bonus, training_effectiveness, init_stats, init_friend_gauge, race_bonus
                 , fan_bonus, hint_levels, hint_freq, specialty_priority, wit_recovery):
        self.name = name
        self.type = type
        self.friendship_bonus = friendship_bonus
        self.mood_effect = mood_effect
        self.stat_bonus = stat_bonus
        self.training_effectiveness = training_effectiveness
        self.init_stats = init_stats
        self.init_friend_gauge = init_friend_gauge
        self.race_bonus = race_bonus
        self.fan_bonus = fan_bonus
        self.hint_levels = hint_levels
        self.hint_freq = hint_freq
        self.specialty_priority = specialty_priority
        self.wit_recovery = wit_recovery

    def get_weight(self):
        # [spd, sta, pwr, gut, wit, none]
        prio = (1 + self.specialty_priority / 100) * .18
        other = .18 - (prio - .18) / 4
        weights = np.ones((6,)) * other
        weights[self.type] = prio
        weights[-1] = 0.1
        return weights

    def get_mood_eff(self):
        return 1 + self.mood_effect / 100

    def get_train_eff(self):
        return 1 + self.training_effectiveness / 100

    def get_friend_eff(self):
        return 1 + self.friendship_bonus / 100

if __name__ == '__main__':
    kitasan = support(type=0,
                      friendship_bonus=25,
                      mood_effect=30,
                      stat_bonus=[0, 0, 1, 0, 0, 0],
                      training_effectiveness=15,
                      init_stats=[0, 0, 0, 0, 0, 0],
                      init_friend_gauge=35,
                      race_bonus=5,
                      fan_bonus=15,
                      hint_levels=2,
                      hint_freq=30,
                      specialty_priority=100,
                      wit_recovery=0)

    print(kitasan.get_weight())
