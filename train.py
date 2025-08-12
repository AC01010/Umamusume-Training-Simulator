import json
import random
import numpy as np
from support_card import support
from tabulate import tabulate

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

def get_training_level(clicks):
    return min(5, (clicks // 4) + 1)


def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))


TURN_PHASES = {
    # Junior Year (turns 0-23)
    0: "Junior Year Pre-Debut, January 1", 1: "Junior Year Pre-Debut, January 2", 2: "Junior Year Pre-Debut, February 1", 3: "Junior Year Pre-Debut, February 2",
    4: "Junior Year Pre-Debut, March 1", 5: "Junior Year Pre-Debut, March 2", 6: "Junior Year Pre-Debut, April 1", 7: "Junior Year Pre-Debut, April 2",
    8: "Junior Year Pre-Debut, May 1", 9: "Junior Year Pre-Debut, May 2", 10: "Junior Year Pre-Debut, June 1", 11: "Junior Year Pre-Debut, June 2",
    12: "Junior Year, July 1", 13: "Junior Year, July 2", 14: "Junior Year, August 1", 15: "Junior Year, August 2",
    16: "Junior Year, September 1", 17: "Junior Year, September 2", 18: "Junior Year, October 1", 19: "Junior Year, October 2",
    20: "Junior Year, November 1", 21: "Junior Year, November 2", 22: "Junior Year, December 1", 23: "Junior Year, December 2",
    
    # Classic Year (turns 24-47)
    24: "Classic Year, January 1", 25: "Classic Year, January 2", 26: "Classic Year, February 1", 27: "Classic Year, February 2",
    28: "Classic Year, March 1", 29: "Classic Year, March 2", 30: "Classic Year, April 1", 31: "Classic Year, April 2",
    32: "Classic Year, May 1", 33: "Classic Year, May 2", 34: "Classic Year, June 1", 35: "Classic Year, June 2",
    36: "Classic Year, July 1", 37: "Classic Year, July 2", 38: "Classic Year, August 1", 39: "Classic Year, August 2",
    40: "Classic Year, September 1", 41: "Classic Year, September 2", 42: "Classic Year, October 1", 43: "Classic Year, October 2",
    44: "Classic Year, November 1", 45: "Classic Year, November 2", 46: "Classic Year, December 1", 47: "Classic Year, December 2",
    
    # Senior Year (turns 48-71)
    48: "Senior Year, January 1", 49: "Senior Year, January 2", 50: "Senior Year, February 1", 51: "Senior Year, February 2",
    52: "Senior Year, March 1", 53: "Senior Year, March 2", 54: "Senior Year, April 1", 55: "Senior Year, April 2",
    56: "Senior Year, May 1", 57: "Senior Year, May 2", 58: "Senior Year, June 1", 59: "Senior Year, June 2",
    60: "Senior Year, July 1", 61: "Senior Year, July 2", 62: "Senior Year, August 1", 63: "Senior Year, August 2",
    64: "Senior Year, September 1", 65: "Senior Year, September 2", 66: "Senior Year, October 1", 67: "Senior Year, October 2",
    68: "Senior Year, November 1", 69: "Senior Year, November 2", 70: "Senior Year, December 1", 71: "Senior Year, December 2",
    
    # URA Finals (turns 72-77)
    72: "URA Finale, Qualifiers 1", 73: "URA Finale, Qualifiers 2",
    74: "URA Finale, Semifinal 1", 75: "URA Finale, Semifinal 2",
    76: "URA Finale, Final 1", 77: "URA Finale, Final 2"
}

SUMMER_TURNS = [36, 37, 38, 39, 60, 61, 62, 63]

MOOD_NAMES = {
    0: "Awful",
    1: "Bad", 
    2: "Normal",
    3: "Good",
    4: "Great"
}

def calculate_failure_rate(training_type, energy_after_training):
    x = energy_after_training

    if x > 35:
        return 0.0    
    if training_type == 4:  # Wit
        rate = 0.000263953 * x**2 - 0.0361337 * x + 0.983803
    else:  # Speed, Stamina, Power, Guts
        rate = 0.000258411 * x**2 - 0.0277237 * x + 0.622712
    
    return max(0.0, rate)  # Ensure failure rate is at least 0%


def sim_training_fail(training_type, energy_after_training):
    failure_rate = calculate_failure_rate(training_type, energy_after_training)
    return random.random() < failure_rate


class Uma:
    def __init__(self, character_data, support_cards):
        self.name = character_data['name']
        self.surfaceAptitude = character_data['surfaceAptitude']
        self.distanceAptitudes = character_data['distanceAptitudes']
        self.strategyAptitudes = character_data['strategyAptitudes']
        self.growthRate = np.array(character_data['growthRate'])
        
        self.energy = 100
        self.maxEnergy = 100
        self.stats = np.array(character_data['baseStats'].copy())
        self.facilityClicks = [0, 0, 0, 0, 0]
        self.mood = 2
        self.fans = 1
        self.turnNo = 0
        self.goodConditions = set()
        self.badConditions = set()
        self.skillPoints = 0

        self.support_cards = support_cards
        self.support_bonds = [0, 0, 0, 0, 0, 0]

        for i, support_card in enumerate(support_cards):
            self.support_bonds[i] = support_card.init_friend_gauge

        self.card_assignment = [[0, 1] for _ in range(6)]

    def assign_supports(self):
        self.card_assignment = [[] for _ in range(6)]
        for i, support_card in enumerate(self.support_cards):
            assigned_facility = np.random.choice(np.arange(6), p=support_card.get_weight())
            self.card_assignment[assigned_facility].append(i)

    def get_training_stats(self, training_type):
        current_turn = self.turnNo

        if current_turn in SUMMER_TURNS:
            level = 5  # Summer training is always level 5
        else:
            level = get_training_level(self.facilityClicks[training_type])

        supp_on_training = self.card_assignment[training_type]

        training_stats = np.array(BASE_STATS[level][training_type])

        # (3, n) array for n support cards, row 0 is mood effect, row 1 is training effect, row 2 is friend effect
        card_effs = [[], [], []]

        flat_bonus = np.zeros(6)

        # get training multipliers
        for support_i in supp_on_training:
            if self.support_cards[support_i].stat_bonus[training_type] >= 1:
                flat_bonus += self.support_cards[support_i].stat_bonus
            card_effs[0].append(self.support_cards[support_i].get_mood_eff())
            card_effs[1].append(self.support_cards[support_i].get_train_eff())
            if self.support_bonds[support_i] >= 80 and self.support_cards[support_i].type == training_type:
                card_effs[2].append(self.support_cards[support_i].get_friend_eff())
            else:
                card_effs[2].append(1)

        effect_vec = np.prod(np.array(card_effs), axis=1)

        multiplier = self.growthRate \
                     * (1 + ((self.mood - 2) * 0.1) * effect_vec[0]) \
                     * effect_vec[1] \
                     * (1 + 0.05 * len(supp_on_training)) \
                     * effect_vec[2]

        stat_changes = ((training_stats[:6] + flat_bonus) * multiplier).astype(int)

        return stat_changes
    
    def train(self, training_type, current_turn=None):
        # Get training level and stats
        if current_turn is None:
            current_turn = self.turnNo
        
        if current_turn in SUMMER_TURNS:
            level = 5  # Summer training is always level 5
        else:
            level = get_training_level(self.facilityClicks[training_type])
        
        training_stats = np.array(BASE_STATS[level][training_type])
        
        # Check for failure (using energy after potential cost)
        energy_after_training = self.energy + training_stats[-1]
        if sim_training_fail(training_type, energy_after_training):
            self._handle_training_failure(training_type)
        else:
            # Successful training - apply energy cost and stat gains
            print("\nTraining success!")

            supp_on_training = self.card_assignment[training_type]

            for support_i in supp_on_training:
                self.support_bonds[support_i] = min(100, self.support_bonds[support_i] + 7)

            self.energy += training_stats[-1]
            self.energy = max(0, self.energy)  # Lower bound at 0

            stat_changes = self.get_training_stats(training_type)

            self.stats += stat_changes

            stat_names = ["Speed", "Stamina", "Power", "Guts", "Intelligence"]
            for i in range(5):
                if training_stats[i] > 0:
                    print(f"{stat_names[i]} went up by {stat_changes[i]}.")
            
            # Display energy change
            energy_cost = abs(training_stats[-1])
            print(f"Energy went down by {energy_cost}.")

            print(f"Skill points went up by {stat_changes[-1]}.")
            
            # Increment facility clicks
            self.facilityClicks[training_type] += 1
    
    def _handle_training_failure(self, training_type):
        # Get failure rate
        failure_rate = calculate_failure_rate(training_type, self.energy)
        
        # Determine worst outcome probability based on failure rate
        if failure_rate >= 0.8:
            worst_outcome_chance = 1.0  # 100%
        elif failure_rate >= 0.2:
            worst_outcome_chance = 0.3  # ~30%
        else:
            worst_outcome_chance = 0.0  # 0%
        
        # Determine if worst outcome occurs
        is_worst_outcome = random.random() < worst_outcome_chance
        
        if is_worst_outcome:
            self._handle_worst_outcome(training_type)
        else:
            self._handle_normal_outcome(training_type)
    
    def _handle_normal_outcome(self, training_type):
        print("\nTraining failed.")
        
        # Get Well Soon! (always choose top option)
        self.mood -= 1
        self.mood = max(0, self.mood)  # Cap mood at minimum 0
        self.stats[training_type] -= 5
        
        print(f"{FACILITY_MAP[training_type]} went down by 5.")
        
        # 8% chance of Poor Practice
        if random.random() < 0.08:
            self.badConditions.add("Poor Practice")
            print("Acquired condition Poor Practice.")
    
    def _handle_worst_outcome(self, training_type):
        print("\nTraining failed badly.")
        
        # Don't Overdo It! (always choose top option)
        self.mood -= 3
        self.mood = max(0, self.mood)  # Cap mood at minimum 0
        self.energy += 10
        self.stats[training_type] -= 10
        
        print(f"{FACILITY_MAP[training_type]} went down by 10.")
        print(f"Energy went up by 10.")
        
        # Reduce 2 random stats by 10 (can include the same trained stat)
        random_stats = random.sample(list(range(5)), 2)
        for stat_idx in random_stats:
            self.stats[stat_idx] -= 10
            print(f"{FACILITY_MAP[stat_idx]} went down by 10.")
        
        # 50% chance of Poor Practice
        if random.random() < 0.5:
            self.badConditions.add("Poor Practice")
            print("Acquired condition Poor Practice.")
    
    def rest(self):
        rand = random.random()
        
        print("\nResting...")
        
        if rand < 0.255:  # 25.5%
            self.energy += 70
            print("Energy went up by 70.")
        elif rand < 0.835:  # 58% (0.255 + 0.58 = 0.835)
            self.energy += 50
            print("Energy went up by 50.")
        elif rand < 0.965:  # 13% (0.835 + 0.13 = 0.965)
            self.energy += 30
            print("Energy went up by 30.")
        else:  # 3.5% (remaining)
            self.energy += 30
            self.badConditions.add("Night Owl")
            print("Energy went up by 30.")
            print("Acquired condition Night Owl.")

        self.energy = min(self.maxEnergy, self.energy)  # Cap energy at max energy
        
    
    def recreation(self):
        rand = random.random()
        
        print("\nRecreation...")
        
        if rand < 0.35:  # 35%
            self.mood += 2  # Karaoke
            print("Karaoke! Mood went up by 2.")
        elif rand < 0.65:  # 30% (0.35 + 0.30 = 0.65)
            self.mood += 1  # Stroll
            self.energy += 10
            print("Stroll! Mood went up by 1.")
            print("Energy went up by 10.")
        elif rand < 0.85:  # 20% (0.65 + 0.20 = 0.85)
            self.mood += 1  # Shrine
            self.energy += 10
            print("Shrine visit (average luck)! Mood went up by 1.")
            print("Energy went up by 10.")
        elif rand < 0.95:  # 10% (0.85 + 0.10 = 0.95)
            self.mood += 1  # Shrine
            self.energy += 20
            print("Shrine visit (good luck)! Mood went up by 1.")
            print("Energy went up by 20.")
        else:  # 5% (remaining)
            self.mood += 1  # Shrine
            self.energy += 30
            print("Shrine visit (great luck)! Mood went up by 1.")
            print("Energy went up by 30.")
        
        # Cap mood at maximum 4
        self.mood = min(4, self.mood)

        # Cap energy at max energy
        self.energy = min(self.maxEnergy, self.energy)
        
    
    def infirmary(self):
        print("\nVisiting infirmary...")
        
        self.energy = min(self.maxEnergy, self.energy + 20)
        print("Energy went up by 20.")
        
        # 85% chance of curing exactly one bad status condition (except "Under the Weather")
        if random.random() < 0.85:
            curable_conditions = [c for c in self.badConditions if c != "Under the Weather"]
            if curable_conditions:
                condition_to_cure = random.choice(curable_conditions)
                self.badConditions.remove(condition_to_cure)
                print(f"Cured condition {condition_to_cure}.")
            else:
                print("No conditions to cure.")
        else:
            print("Treatment was not effective this time.")
        
    
    def rest_and_recreation(self):
        print("\nRest and recreation...")
        
        self.energy += 40
        self.mood += 1
        
        print("Energy went up by 40.")
        print("Mood went up by 1.")
        
        # Cap mood at maximum 4
        self.mood = min(4, self.mood)
        
        # Cap energy bounds
        self.energy = min(self.maxEnergy, self.energy)

    def displayStats(self):
        print()
        print(f"📅 {TURN_PHASES.get(self.turnNo, 'Unknown Turn')}")
        
        # Create energy bar with percentage
        energy_percentage = int((self.energy / self.maxEnergy) * 100)
        bar_length = 40
        filled_blocks = int((self.energy / self.maxEnergy) * bar_length)
        energy_bar = "█" * filled_blocks + "▒" * (bar_length - filled_blocks)
        
        print(f"\nEnergy: [ {energy_bar} ] {energy_percentage}% | Mood: {MOOD_NAMES.get(self.mood, 'Unknown')}")

        headers = ['Speed', 'Stamina', 'Power', 'Guts', 'Wit', 'Skill Pts']
        vals = self.stats.reshape((1, -1))

        print(tabulate(vals, headers=headers, tablefmt='rounded_outline'))

        if self.goodConditions or self.badConditions:
            all_conditions = list(self.goodConditions) + list(self.badConditions)
            print(f"\nConditions: {', '.join(all_conditions)}")
        else:
            print(f"\nConditions: None")
    
    def displayTurn(self, current_turn):
        options = []
        
        if current_turn in SUMMER_TURNS:
            # Summer turns only have Train and Rest and Recreation
            options.append("Train")
            options.append("Rest and Recreation")
        else:
            # Non-summer turns
            options.append("Train")
            options.append("Rest")
            options.append("Recreation")
            
            # Infirmary only if there are bad conditions that aren't "Under the Weather"
            curable_conditions = [c for c in self.badConditions if c != "Under the Weather"]
            if curable_conditions:
                options.append("Infirmary")
        
        # Display options
        for i, option in enumerate(options, 1):
            print(f"{i}) {option}")
        
        while True:
            try:
                choice = int(input("Choose an option: "))
                if 1 <= choice <= len(options):
                    return choice - 1, options[choice - 1]  # Return 0-indexed choice and option name
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
    
    def displayTraining(self):
        print("\n--- Training Options ---")
        training_options = ["Speed", "Stamina", "Power", "Guts", "Intelligence"]
        
        for i, training in enumerate(training_options):
            if self.turnNo in SUMMER_TURNS:
                level = 5
            else:
                level = get_training_level(self.facilityClicks[i])
            
            training_stats = self.get_training_stats(i)
            energy_after = self.energy + training_stats[-1]  # Add energy cost (negative)
            failure_rate = min(100, calculate_failure_rate(i, energy_after) * 100) # Cap display at 100%
            
            # Display stats that will be gained
            stat_gains = []
            stat_names = ["Speed", "Stamina", "Power", "Guts", "Intelligence"]
            for j in range(5):
                if training_stats[j] > 0:
                    stat_gains.append(f"+{training_stats[j]} {stat_names[j]}")
            
            skill_pts = training_stats[5] if len(training_stats) > 5 else 0

            supp_on_facility = [self.support_cards[a].name for a in self.card_assignment[i]]
            bonds_on_facility = [self.support_bonds[a] for a in self.card_assignment[i]]

            print(f"{i+1}) {training} (Lv{level})")
            print(f'   Supports: {list(zip(supp_on_facility, bonds_on_facility))}')
            print(f"   Stats: {', '.join(stat_gains) if stat_gains else 'None'}")
            print(f"   Skill Pts: +{skill_pts}")
            print(f"   Energy After: {max(0, energy_after)}")
            print(f"   Failure Rate: {failure_rate:.1f}%")
        
        while True:
            try:
                choice = int(input("Choose training type: "))
                if 1 <= choice <= len(training_options):
                    return choice - 1  # Return 0-indexed choice
                else:
                    print(f"Please enter a number between 1 and {len(training_options)}")
            except ValueError:
                print("Please enter a valid number")
    
    def turn(self):
        # Display large banner for current turn's date
        current_turn_phase = TURN_PHASES.get(self.turnNo, 'Unknown Turn')
        print("\n" + "="*60)
        print(f"🗓️  {current_turn_phase}  🗓️".center(60))
        print("="*60)
        
        # Display current stats
        self.displayStats()
        self.assign_supports()
        # print(f'Speed: {[self.support_cards[i].name for i in self.card_assignment[0]]} '
        #       f'Stamina: {[self.support_cards[i].name for i in self.card_assignment[1]]} '
        #       f'Power: {[self.support_cards[i].name for i in self.card_assignment[2]]} '
        #       f'Guts: {[self.support_cards[i].name for i in self.card_assignment[3]]} '
        #       f'Wit: {[self.support_cards[i].name for i in self.card_assignment[4]]}')
        
        # Get turn options and choice
        _, option_name = self.displayTurn(self.turnNo)
        
        # Execute the chosen action
        if option_name == "Train":
            # Display stats again before training selection
            self.displayStats()
            training_choice = self.displayTraining()
            self.train(training_choice, self.turnNo)
        elif option_name == "Rest":
            self.rest()
        elif option_name == "Recreation":
            self.recreation()
        elif option_name == "Rest and Recreation":
            self.rest_and_recreation()
        elif option_name == "Infirmary":
            self.infirmary()
        
        # Increment turn counter
        self.turnNo += 1
        
        # Check if training is complete (turn 72 is the last training turn)
        if self.turnNo >= 72:
            print(f"\n🎉 Training complete! Moving to URA Finals...")
            return False  # End training phase
        
        return True  # Continue training


def load_character(character_name):
    with open('character.json', 'r') as f:
        characters = json.load(f)
    
    for character in characters:
        if character['name'] == character_name:
            return character
    
    raise ValueError(f"Character '{character_name}' not found")


def main():
    character_data = load_character("Sakura Bakushin O")
    kitasan = support(name='Kitasan Black',
                      type=0,
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

    super_boob = support(name='Super Boob',
                         type=1,
                         friendship_bonus=37.5,
                         mood_effect=0,
                         stat_bonus=[0, 1, 0, 0, 0, 0],
                         training_effectiveness=15,
                         init_stats=[0, 35, 0, 0, 0, 0],
                         init_friend_gauge=30,
                         race_bonus=10,
                         fan_bonus=20,
                         hint_levels=0,
                         hint_freq=0,
                         specialty_priority=55,
                         wit_recovery=0)

    uma = Uma(character_data, [kitasan, super_boob])

    
    print(f"🏇 Welcome to Umamusume Training Simulator! 🏇")
    
    # Main game loop
    while uma.turn():
        pass  # The turn() function handles everything and returns False when done
    
    # Final stats display
    print(f"\n🏁 Final Stats for {uma.name} 🏁")
    uma.displayStats()


if __name__ == "__main__":
    main()
