import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
from enum import Enum
from train import Uma, load_character, load_support_card, SUMMER_TURNS, clamp
import numpy as np

# Register this module as a gym environment. Once registered, the id is usable in gym.make().
# When running this code, you can ignore this warning: "UserWarning: WARN: Overriding environment airplane-boarding-v0 already in registry."
register(
    id='uma-trainer-v1',
    entry_point='uma_trainer:UmaEnv', # module_name:class_name
)

ACTION_MAP = {
    0: ('train', 0), #train speed
    1: ('train', 1), #train stamina
    2: ('train', 2), #train power
    3: ('train', 3), #train guts
    4: ('train', 4), #train wisdom
    5: ('rest', None),
    6: ('recreation', None),
    7: ('infirmary', None),
    8: ('rest_and_recreation', None)
}

KNOWN_CONDITIONS = [
    'Poor Practice',
    'Night Owl',
    'Under the Weather'
]

class UmaEnv(gym.Env):
    metadata = {'render_modes': ['human','terminal'], 'render_fps': 1}

    def __init__(self, render_mode=None, character_name='Sakura Bakushin O', support_cards=None):
        super().__init__()
        if support_cards is None:
            support_cards = ['Kitasan Black', 'Super Creek']
        self.render_mode = render_mode
        self.character_name = character_name
        self.support_cards = support_cards

        self.uma = None

        self.action_space = spaces.Discrete(len(ACTION_MAP))

        self.observation_space = spaces.Dict({
            'stats': spaces.Box(low=0.0, high=1200, shape=(6,), dtype=np.float32), # speed, stamina, power, guts, wisdom, skill_pts
            'energy': spaces.Box(low=0.0, high=100, shape=(1,), dtype=np.float32),
            'mood': spaces.Box(low=0.0, high=4, shape=(1,), dtype=np.float32),
            'turns_no': spaces.Box(low=0.0, high=72, shape=(1,), dtype=np.float32),
            'stats_increase': spaces.Box(low=0.0, high=100, shape=(5,7), dtype=np.float32), #stats increase is a 5x7 array, each row is a stat increase from a training type with failure rate as the last index
            'support_bond': spaces.Box(low=0.0, high=100, shape=(6,), dtype=np.float32), # support bond levels for 6 support characters
            'conditions': spaces.MultiBinary(len(KNOWN_CONDITIONS)),
        })

    def reset(self, seed=None, options=None):
        super().reset(seed=seed) # gym requires this call to control randomness and reproduce scenarios.

        character = load_character(self.character_name)
        support_cards = [load_support_card(name) for name in self.support_cards]
        self.uma = Uma(character, support_cards)
        self.render()

        return self._get_obs(), {}

    def _get_obs(self):
        #uma's current stat line
        stats = self.uma.stats
        energy = self.uma.energy
        mood = self.uma.mood
        turns_no = self.uma.turnNo
        stats_increase = self.uma.getTrainingIncrease()
        support_bond = self.uma.support_bonds
        conditions = np.array([1 if cond in self.uma.badConditions else 0 for cond in KNOWN_CONDITIONS], dtype=np.int8)

        return {
            'stats': np.array(stats, dtype=np.float32),
            'energy': np.array([energy], dtype=np.float32),
            'mood': np.array([mood], dtype=np.float32),
            'turns_no': np.array([turns_no], dtype=np.float32),
            'stats_increase': np.array(stats_increase, dtype=np.float32),
            'support_bond': np.array(support_bond, dtype=np.float32),
            'conditions': conditions,
        }

    def step(self, action):
        action = int(action)
        action_type, action_arg = ACTION_MAP[action]
        reward = 0.0
        terminated = False
        truncated = False
        info = {}

        previous_obs = self._get_obs()

        # Perform action
        if action_type == "train":
            self.uma.train(action_arg, current_turn=self.uma.turnNo)
        elif action_type == "rest":
            self.uma.rest()
        elif action_type == "recreation":
            self.uma.recreation()
        elif action_type == "infirmary":
            self.uma.infirmary()
        elif action_type == "rest_and_recreation":
            self.uma.rest_and_recreation()

        self.uma.turnNo += 1

        if self.uma.turnNo >= 72:
            terminated = True

        reward = self._calculate_reward(previous_obs)
        obs = self._get_obs()
        return obs, reward, terminated, truncated, info

    def _calculate_reward(self, prev_obs):
        curr_obs = self._get_obs()

        speed_increase = curr_obs['stats'][0] - prev_obs['stats'][0]
        reward = clamp(speed_increase / 100.0, -1.0, 1.0)
        return reward

    def render(self):
        if self.render_mode is None:
            return

        if self.render_mode == 'human':
            self.uma.displayTraining()
        elif self.render_mode == 'terminal':
            self.uma.displayStats()
        else:
            raise ValueError(f"Unsupported render mode: {self.render_mode}")

    # This method is used to mask the actions that are allowed
    # action_masks() is the function signature required by the MaskablePPO class
    def action_masks(self) -> list[bool]:
        mask = []

        #Always allow the first 5 training options + rest + recreation
        for i in range(7):
            mask.append(True)

        #Infirmary is only available if there is a bad condition
        if len(self.uma.badConditions) > 0:
            mask.append(True)
        else:
            mask.append(False)

        #Rest and recreation is only available if the turn no is in the summer
        if self.uma.turnNo in SUMMER_TURNS:
            mask.append(True)
        else:
            mask.append(False)

        return mask


def my_check_env():
    from gymnasium.utils.env_checker import check_env
    env = gym.make('uma-trainer-v1', render_mode='terminal')
    check_env(env.unwrapped)


if __name__ == "__main__":
    #my_check_env()
    env = gym.make('uma-trainer-v1', render_mode='terminal')

    observation, _ = env.reset()
    terminated = False
    total_reward = 0
    step_count = 0

    while not terminated:
        # Choose random action
        action = env.action_space.sample()

        # Skip action if invalid
        masks = env.unwrapped.action_masks()
        print(action)
        if (masks[action] == False):
            continue

        # Perform action
        observation, reward, terminated, _, _ = env.step(action)
        total_reward += reward

        step_count += 1

        print(f"Step {step_count} Action: {action}")
        print(f"Observation: {observation}")
        print(f"Reward: {reward}\n")

    print(f"Total Reward: {total_reward}")
