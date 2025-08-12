import gymnasium as gym
import numpy as np
from train import Uma, load_character, SUMMER_TURNS
from gymnasium import spaces
from gymnasium.envs.registration import register
from typing import Tuple, Dict, Any

register(
    id='UmaTrainer-v0',
    entry_point='uma_trainer:UmaTrainerEnv',
)

#Observation caps
STAT_CAP = 1200.0
ENERGY_CAP = 100.0
MOOD_CAP = 4.0
SKILL_PT_CAP = 2000
TURNS_CAP = 77

KNOWN_CONDITIONS = [
    'Poor Practice',
    'Night Owl',
    'Under the Weather'
]

ACTION_MAP = {
    0: ('train', 0),
    1: ('train', 1),
    2: ('train', 2),
    3: ('train', 3),
    4: ('train', 4),
    5: ('rest', None),
    6: ('recreation', None),
    7: ('infirmary', None),
    8: ('rest_and_recreation', None)
}

class UmaTrainerEnv(gym.Env):
    metadata = {'render_modes': ['human'], 'render_fps': 1}

    def __init__(self, render_mode=None, character_name='Sakura Bakushin O'):
        super().__init__()
        self.render_mode = render_mode
        self.character_name = character_name

        self.uma = None

        #9 actions for 5 training types + rest + recreation + infirmary + rest_and_recreation
        self.action_space = spaces.Discrete(len(ACTION_MAP))

        #Observatoin space is just the uma's stats, energy, mood, skill points, turn number, and conditions
        self.observation_space = spaces.Dict({
            'stats': spaces.Box(low=0, high=STAT_CAP, shape=(5,), dtype=np.float32),
            'energy': spaces.Box(low=0, high=ENERGY_CAP, shape=(1,), dtype=np.float32),
            'mood': spaces.Box(low=0, high=MOOD_CAP, shape=(1,), dtype=np.float32),
            'skill_points': spaces.Box(low=0, high=SKILL_PT_CAP, shape=(1,), dtype=np.float32),
            'turns_no': spaces.Box(low=0, high=TURNS_CAP, shape=(1,), dtype=np.int32),
            'conditions': spaces.MultiBinary(len(KNOWN_CONDITIONS)),
        })

    def reset(self, *, seed=None, options=None) -> Tuple[Dict[str, Any], Dict]:
        super().reset(seed=seed)
        character = load_character(self.character_name)
        self.uma = Uma(character)

        observation = {
            'stats': np.array(self.uma.stats, dtype=np.float32),
            'energy': np.array([self.uma.energy], dtype=np.float32),
            'mood': np.array([self.uma.mood], dtype=np.float32),
            'skill_points': np.array([self.uma.skillPoints], dtype=np.float32),
            'turns_no': np.array([self.uma.turnNo], dtype=np.int32),
            'conditions': np.array([1 if condition in self.uma.badConditions else 0 for condition in KNOWN_CONDITIONS], dtype=np.int8)
        }
        info = {"character": self.character_name, "turns_no": self.uma.turnNo}
        return observation, info

    def step(self, action):
        assert self.action_space.contains(action), f"Invalid action {action}"

        action_type, action_arg = ACTION_MAP[action]
        prev_stats = np.array(self.uma.stats, dtype=np.float32).copy()
        prev_energy = self.uma.energy
        prev_mood = self.uma.mood
        prev_skill_points = self.uma.skillPoints  # fixed attribute name

        # Execute action (note: use correct parameter name current_turn)
        if action_type == "train":
            self.uma.train(action_arg, current_turn=self.uma.turnNo)  # fixed arg name
        elif action_type == "rest":
            self.uma.rest()
        elif action_type == "recreation":
            self.uma.recreation()
        elif action_type == "infirmary":
            self.uma.infirmary()
        elif action_type == "rest_and_recreation":
            # if you want to enforce summer-only, you can penalize otherwise; here we call the proper method
            if self.uma.turnNo in SUMMER_TURNS:
                self.uma.rest_and_recreation()
            else:
                # fallback: do a normal rest (or you could raise)
                self.uma.rest()

        # advance the turn counter (same semantics as your original code)
        self.uma.turnNo += 1

        # Reward logic (fixed the sign check for stat gain)
        reward = 0.0
        # Was: prev_stats[0] - self.uma.stats[0] > 0  (this tested for decrease). Fixed:
        speed_gain = float(self.uma.stats[0] - prev_stats[0])

        if action_type == "train" and action_arg == 0 and prev_energy > 50 and speed_gain > 0:
            reward += 35.0
        elif action_type == "rest" and prev_energy < 50:
            reward += 60.0
        elif action_type == "recreation" and prev_mood < 4:
            reward += 10.0
        else:
            reward -= 80.0

        if action_type != "rest" and prev_energy < 50:
            reward -= 50.0

        terminated = False
        truncated = False
        info = {"character": self.character_name, "turns_no": self.uma.turnNo}

        # termination: original simulation used 72 as last training turn; choose >=72
        if self.uma.turnNo >= 72:
            terminated = True
            reward += float(self.uma.stats[0]) / 10.0
            info["final_stats"] = self.uma.stats

        obs = {
            'stats': np.array(self.uma.stats, dtype=np.float32),
            'energy': np.array([self.uma.energy], dtype=np.float32),
            'mood': np.array([self.uma.mood], dtype=np.float32),
            'skill_points': np.array([self.uma.skillPoints], dtype=np.float32),
            'turns_no': np.array([self.uma.turnNo], dtype=np.int32),
            'conditions': np.array([1 if condition in self.uma.badConditions else 0 for condition in KNOWN_CONDITIONS], dtype=np.int8)
        }
        return obs, float(reward), terminated, truncated, info

    def render(self):
        if self.uma:
            self.uma.displayStats()

#Check validity of environment
def my_check_env():
    from gymnasium.utils.env_checker import check_env
    env = gym.make('UmaTrainer-v0', render_mode=None)
    check_env(env.unwrapped)

if __name__ == '__main__':
    #my_check_env()

    env = gym.make('UmaTrainer-v0', render_mode=None, character_name='Sakura Bakushin O')
    observation, info = env.reset()
    terminated = False
    total_reward =0.0
    step_count = 0

    while not terminated:
        #Choose a random action
        action = env.action_space.sample()

        #Perform action
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        step_count += 1
        print(f"Step: {step_count}, Action: {action}, Reward: {reward}, Total Reward: {total_reward}")
    print(f"Final Stats: {info.get('final_stats', 'N/A')}, Total Reward: {total_reward}")