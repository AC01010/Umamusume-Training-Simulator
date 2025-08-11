# train_dqn_uma.py
import gymnasium as gym
from gymnasium.wrappers import FlattenObservation
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor
import numpy as np
from typing import Tuple
import uma_trainer

# ---------------------------
# Hyperparameters / tuning
# ---------------------------
TOTAL_TIMESTEPS = 200_000
LEARNING_RATE = 1e-4
BATCH_SIZE = 64
BUFFER_SIZE = 100_000
TRAIN_FREQ = 4
TARGET_UPDATE_INTERVAL = 1000

# Reward shaping parameters
SPEED_SHAPING_ALPHA = 0.04      # reward per speed point gained this step (tune)
TERMINAL_BONUS = 5.0            # extra reward scaled by speed/1200 at episode end
SPEED_TARGET = 1200.0

# environment id (ensure registered / available)
ENV_ID = "UmaTrainer-v0"
CHARACTER_NAME = "Sakura Bakushin O"


# ---------------------------
# Env creation function for DummyVecEnv
# ---------------------------
def make_env():
    def _init():
        # base env from your registration; pass character name
        # IMPORTANT: SpeedRewardWrapper must come BEFORE FlattenObservation
        base = gym.make(ENV_ID, character_name=CHARACTER_NAME)
        # flatten observations (dict -> 1D Box)
        flat = FlattenObservation(base)
        # Monitor to record episode stats (optional but useful)
        monitored = Monitor(flat)
        return monitored
    return _init

# ---------------------------
# Training
# ---------------------------
def train():
    # create vectorized env (single-env DummyVecEnv)
    venv = DummyVecEnv([make_env()])
    # normalize observations (optional but often helps)
    venv = VecNormalize(venv, norm_obs=True, norm_reward=False)

    # DQN model
    model = DQN(
        "MlpPolicy",
        venv,
        learning_rate=LEARNING_RATE,
        buffer_size=BUFFER_SIZE,
        learning_starts=2000,
        batch_size=BATCH_SIZE,
        gamma=0.99,
        train_freq=TRAIN_FREQ,
        target_update_interval=TARGET_UPDATE_INTERVAL,
        verbose=1,
    )

    # training
    model.learn(total_timesteps=TOTAL_TIMESTEPS)
    model.save("dqn_uma_speed")
    venv.close()
    return model

# ---------------------------
# Evaluation
# ---------------------------
def evaluate(model, n_eps=20):
    # build a non-vectorized env for evaluation (but same wrappers)
    env = gym.make(ENV_ID, character_name=CHARACTER_NAME)
    env = FlattenObservation(env)

    final_speeds = []
    total_rewards = []
    for ep in range(n_eps):
        obs, _ = env.reset()
        done = False
        ep_reward = 0.0
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            print(action)
            obs, r, terminated, truncated, info = env.step(int(action))
            ep_reward += float(r)
            done = terminated or truncated
        total_rewards.append(ep_reward)
        # info might contain final_stats at termination (if your env sets it)
        final_stats = info.get("final_stats", None)
        if final_stats is not None:
            final_speeds.append(float(final_stats[0]))
        else:
            # fallback: pull speed from last obs
            final_speeds.append(float(obs[0]))  # because obs is flattened, but not robust
    env.close()
    print(f"Eval over {n_eps} eps -> avg reward: {np.mean(total_rewards):.2f}, avg final speed: {np.mean(final_speeds):.1f}")

if __name__ == "__main__":
    #model = DQN.load("dqn_uma_speed")
    model = train()
    evaluate(model, n_eps=10)
