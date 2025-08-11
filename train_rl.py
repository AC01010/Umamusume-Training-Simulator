# qlearn_umamusume.py
import json
import random
import math
from collections import defaultdict
from copy import deepcopy
from train import Uma, load_character, SUMMER_TURNS, TURN_PHASES

# ---- Paste your Uma class and constants here (BASE_STATS, FACILITY_MAP, SUMMER_TURNS, TURN_PHASES, etc.)
# For brevity in this snippet I assume you've imported the Uma and helper functions from your existing file:
# from your_sim_file import Uma, load_character, SUMMER_TURNS, TURN_PHASES
# If you keep everything in one file, ensure Uma class definition appears above the environment & training code.

# For standalone usage, load the Uma and helper definitions above this code block.

# ---------- Environment wrapper ----------
class UmaEnv:
    """
    Minimal environment wrapper around Uma object for RL.
    Actions:
      0-4 => Train (Speed, Stamina, Power, Guts, Wit)
      5   => Rest
      6   => Recreation
      7   => Rest and Recreation
      8   => Infirmary
    """
    ACTIONS = [
        "train_speed", "train_stamina", "train_power", "train_guts", "train_wit",
        "rest", "recreation", "rest_and_recreation", "infirmary"
    ]

    def __init__(self, character_data, seed=None):
        self.char_template = character_data
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.max_turns = 72
        self.reset()

    def reset(self):
        # Recreate Uma from template to start new episode
        self.uma = Uma(deepcopy(self.char_template))
        # ensure deterministic seed per episode if requested
        if self.seed is not None:
            # re-seed to get repeatability if desired (optional)
            random.seed(self.seed)
        # initial state
        return self._get_state()

    def _get_state(self):
        """
        Discretize a small set of features into a tuple state.
        Features used:
          - remaining_turns_bucket (progress)
          - speed_bucket
          - energy_bucket
          - speed_facility_click_bucket
        """
        # raw features
        speed = self.uma.stats[0]
        energy = self.uma.energy
        turn = self.uma.turnNo
        clicks_speed = self.uma.facilityClicks[0]

        # Buckets -- tune ranges if needed
        # speed buckets: step 20 from 800 to 1200 (covers many typical ranges). Adjust if needed.
        speed_bucket = int((speed - 800) // 20)
        speed_bucket = max(0, min(20, speed_bucket))

        # energy buckets 0-100 step 10 -> 0..10
        energy_bucket = int(energy // 10)
        energy_bucket = max(0, min(10, energy_bucket))

        # turn progress bucket (0..11)
        turn_bucket = int(turn // 6)
        turn_bucket = max(0, min(11, turn_bucket))

        # facility clicks bucket for speed: 0..5
        clicks_bucket = min(5, clicks_speed)

        return (turn_bucket, speed_bucket, energy_bucket, clicks_bucket)

    def step(self, action):
        """
        Apply action (index) to the Uma instance.
        Returns: next_state, reward, done, info

        Behavior implemented:
          - Penalize resting-like actions (5,6,7,8) if pre-action energy > 50
          - Penalize training actions (0..4) if pre-action energy < 45
          - Reward Rest (5) when pre-action energy < 45
          - Reward Recreation (6) when pre-action mood != Great
          - Extra reward for choosing Speed training (action == 0) based on expected immediate speed gain
        """
        prev_speed = self.uma.stats[0]
        done = False
        info = {}

        # Pre-action observations (used for penalties/rewards)
        pre_action_energy = self.uma.energy
        pre_action_mood = self.uma.mood


        #Unsure if valid

        # --- Execute action ---
        if action in range(0, 5):
            # Training actions
            self.uma.train(action, current_turn=self.uma.turnNo)
        elif action == 5:
            self.uma.rest()
        elif action == 6:
            self.uma.recreation()
        elif action == 7:
            self.uma.rest_and_recreation()
        elif action == 8:
            self.uma.infirmary()
        else:
            raise ValueError("Invalid action index")

        # Advance turn
        self.uma.turnNo += 1
        if self.uma.turnNo >= self.max_turns:
            done = True

        # Penalties (tunable)
        rest_penalty = -6.0  # penalty for unnecessary rest-like actions (when energy > 50)
        train_low_energy_penalty = -2.5  # penalty for attempting to train with low energy (<50)

        # Positive bonuses (tunable)
        rest_reward = 4.0  # reward for resting when energy < 45
        recreation_reward = 10.0  # reward for recreation when mood is not Great

        # Speed-action-specific reward (choosing Speed)
        # We give a bonus based on the *expected* immediate speed gain (so choosing Speed is rewarded even if it fails)
        # multiplier controls how strongly we prefer choosing Speed; tune as needed.
        speed_action_bonus = 0.0
        if action == 0:
            speed_action_bonus = 6

        penalty = 0.0
        bonus = 0.0

        other_training_penalty = -20.0  # penalty for training other stats (1-4) when speed is the main goal

        if action in range(1, 5):
            # Penalize training other stats when speed is the main goal
            penalty += other_training_penalty

        # Rest-like penalty includes Infirmary (action 8) as requested
        if action in (5, 6, 7, 8) and pre_action_energy > 50:
            penalty += rest_penalty

        # Training penalty when low energy
        if action in range(0, 5) and pre_action_energy < 50:
            penalty += train_low_energy_penalty

        # Reward Rest if energy is low
        if action == 5 and pre_action_energy < 45:
            bonus += rest_reward

        # Reward Recreation if mood is not "Great" (mood != 4)
        if action == 6 and pre_action_mood != 4:
            bonus += recreation_reward

        # Add speed-action-specific bonus
        bonus += speed_action_bonus


        reward = penalty + bonus
        next_state = self._get_state()
        return next_state, reward, done, info

    def action_space_n(self):
        return len(self.ACTIONS)

    def sample_random_action(self):
        return random.randrange(self.action_space_n())

# ---------- Q-learning Training ----------
def q_learning_train(env, episodes=2000, alpha=0.1, gamma=0.99, epsilon=1.0, eps_min=0.05, eps_decay=0.9995):
    n_actions = env.action_space_n()
    Q = defaultdict(lambda: [0.0] * n_actions)

    for ep in range(episodes):
        state = env.reset()
        done = False

        # optionally decay epsilon per episode
        if ep % 1 == 0:
            epsilon = max(eps_min, epsilon * eps_decay)

        while not done:
            # epsilon-greedy
            if random.random() < epsilon:
                action = random.randrange(n_actions)
            else:
                # pick argmax
                qvals = Q[state]
                maxv = max(qvals)
                # break ties randomly
                best_actions = [i for i, v in enumerate(qvals) if v == maxv]
                action = random.choice(best_actions)

            next_state, reward, done, _ = env.step(action)

            # Q update
            old_q = Q[state][action]
            if not done:
                next_max = max(Q[next_state])
            else:
                next_max = 0.0
            Q[state][action] = old_q + alpha * (reward + gamma * next_max - old_q)

            state = next_state

        # (optional) print progress occasionally
        if (ep + 1) % (episodes // 10) == 0:
            print(f"Episode {ep + 1}/{episodes}  epsilon={epsilon:.4f}")

    return Q

# ---------- Evaluate learned policy ----------
def evaluate_policy(env, Q, episodes=50):
    best_final_speeds = []
    best_final_stat_lines = []
    for _ in range(episodes):
        state = env.reset()
        done = False
        while not done:
            qvals = Q[state]
            maxv = max(qvals)
            best_actions = [i for i, v in enumerate(qvals) if v == maxv]
            action = random.choice(best_actions)
            state, _, done, _ = env.step(action)

        # episode end
        final_speed = env.uma.stats[0]
        best_final_speeds.append(final_speed)
        best_final_stat_lines.append( (final_speed, env.uma.stats, env.uma.skillPoints) )

    # summary
    avg = sum(best_final_speeds) / len(best_final_speeds)
    best = max(best_final_speeds)
    worst = min(best_final_speeds)
    print(f"Evaluation over {episodes} episodes: avg speed={avg:.2f}, best={best}, worst={worst}")
    # show best outcome details
    best_idx = best_final_speeds.index(best)
    print("Best final stat line (speed, stats[], skillPoints):")
    print(best_final_stat_lines[best_idx])
    return best_final_stat_lines

# ---------- Helper to load character ----------
def load_character(filename, character_name):
    with open(filename, 'r') as f:
        characters = json.load(f)
    for character in characters:
        if character['name'] == character_name:
            return character
    raise ValueError(f"Character '{character_name}' not found in {filename}")

# ---------- Main execution ----------
if __name__ == "__main__":
    # ensure deterministic behavior across runs (optional)
    SEED = 42
    random.seed(SEED)

    # load your character JSON (same format as your original load_character)
    character_data = load_character('character.json', "Sakura Bakushin O")

    env = UmaEnv(character_data, seed=SEED)

    # training hyperparams you can tune
    episodes = 3000
    alpha = 0.15
    gamma = 0.99
    epsilon = 1.0
    eps_min = 0.05
    eps_decay = 0.9992

    print("Starting Q-learning training...")
    Q = q_learning_train(env, episodes=episodes, alpha=alpha, gamma=gamma,
                         epsilon=epsilon, eps_min=eps_min, eps_decay=eps_decay)

    print("\nTraining complete. Evaluating learned policy (greedy)...")
    evaluate_policy(env, Q, episodes=100)

    # Optionally run one deterministic rollout and print turns to inspect actions
    print("\nGreedy rollout (inspect):")
    s = env.reset()
    done = False
    step_no = 0
    while not done:
        qvals = Q[s]
        action = max(range(len(qvals)), key=lambda i: qvals[i])
        print(f"Turn {env.uma.turnNo:02d}: action={UmaEnv.ACTIONS[action]}, Speed={env.uma.stats[0]}, Energy={env.uma.energy}, Clicks={env.uma.facilityClicks}")
        s, _, done, _ = env.step(action)
        step_no += 1
    print("\nFinal stats:")
    print(f"Speed={env.uma.stats[0]}, Full stats={env.uma.stats}, SkillPoints={env.uma.skillPoints}")
