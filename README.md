# Umamusume Training Simulator

A Python-based simulator for Umamusume Pretty Derby training mechanics, focusing on accurate stat growth, failure rates, and support card interactions.

## Installation
`pip install -r requirements.txt`
Suggestion: use Python venv (`python -m venv uma-venv` before installation, then on every terminal spawn `source ./uma-venv/scripts/activate` or whatever platform-specific activation script)

## Project Structure

- `sage_sim/` - Contains an old version of the simulator (will be deleted later)
- `character.json` - Character data including base stats, growth rates, and aptitudes
- `support_cards.json` - Support card definitions with bonuses and effects
- `train.py` - Main simulator file with core classes and functions
- `support_card.py` - Support card class implementation

## Reinforced Learning Structure
- `uma_trainer.py` - Gymnasium environment wrapped around the simulator for reinforcement learning
- `train_rl.py` - RL training script using Stable Baselines3 MaskablePPO algorithm
- `models/` - Directory for saving trained RL models
- `logs/` - Directory for tensorboard logs and training metrics

## API Structure

The simulator is built around two main classes:

- **`Uma`**: The primary character class handling training mechanics, stat calculations, and turn progression
- **`support`**: Support card class with bonuses, effects, and facility assignment logic

Key functions include `load_character()` and `load_support_card()` for loading data from JSON files, plus various utility functions for failure rates and stat calculations.

## Implemented Mechanics

### Training System
- **Base Training Stats**: 5 levels per facility with predefined stat gains
- **Summer Training**: Always level 5 training during summer turns
- **Failure System**: Quadratic failure rate based on post-training energy
- **Stat Calculation**: Complex multiplier system incorporating growth rates, mood, support effects

### Failure Rate Formula
Training failure rates are modeled using quadratic equations fitted from in-game data:

**For Speed/Stamina/Power/Guts:**
$$P_{\text{fail}} = 0.000258411 \cdot E^2 - 0.0277237 \cdot E + 0.622712$$

**For Intelligence (Wit):**
$$P_{\text{fail}} = 0.000263953 \cdot E^2 - 0.0361337 \cdot E + 0.983803$$

Where $E$ is energy after training. Failure rates cap at 0% when $E > 35$.

### Stat Growth Formula
Training stat gains follow this formula:

$$S = (B + F) \cdot G \cdot M \cdot T \cdot P \cdot \text{Fr}$$

Where:
- $S$ = Final stat gain
- $B$ = Base training stat
- $F$ = Flat bonus from support cards
- $G$ = Character growth rate
- $M$ = Mood multiplier: $1 + (\text{mood} - 2) \cdot 0.1 \cdot \text{moodEffect}$
- $T$ = Training effectiveness: $1 + \text{trainingEff}/100$
- $P$ = Partner bonus: $1 + 0.05 \cdot \text{numPartners}$
- $\text{Fr}$ = Friend bonus: $1 + \text{friendshipBonus}/100$ (when bond ≥ 80)

### Support Card Assignment
Support cards are assigned to facilities each turn based on weighted probabilities:

$$P_{\text{facility}} = \begin{cases}
0.18 \cdot (1 + \text{specialtyPriority}/100) & \text{if specialty facility} \\
0.18 - \frac{\text{specialtyBonus}}{4} & \text{if other facility} \\
0.1 & \text{if no facility}
\end{cases}$$

### Activity Probabilities

**Rest Outcomes:**
- 70 energy: 25.5%
- 50 energy: 58.0%
- 30 energy: 13.0%
- 30 energy + Night Owl: 3.5%

**Recreation Outcomes:**
- Karaoke (+2 mood): 35%
- Stroll (+1 mood, +10 energy): 30%
- Shrine (average, +1 mood, +10 energy): 20%
- Shrine (good, +1 mood, +20 energy): 10%
- Shrine (great, +1 mood, +30 energy): 5%

**Infirmary:**
- 85% chance to cure one random bad condition (except "Under the Weather")
- Always grants +20 energy

### Training Failures
- **Normal Failure**: -1 mood, -5 to trained stat, 8% chance of Poor Practice
- **Severe Failure**: -3 mood, +10 energy, -10 to trained stat, -10 to 2 random stats, 50% chance of Poor Practice

## Not Implemented

The following Umamusume mechanics are **not** currently implemented:

### Core Gameplay
- **Racing System**: Race participation, results, rewards, and performance calculations
- **Random Events**: Support card events, trainee interactions, seasonal events
- **Skill System**: Learning, upgrading, and using racing skills
- **Legacy/Factor System**: Stat inheritance from previous generations

### Support Card Features
- Support card events and story dialogues
- Hint system for skill acquisition
- Special training bonuses and effects

## Data Sources

- **Failure Rate Curves**: Fitted from energy sampling data from JP server gameplay
- **Probability Distributions**: Based on samples from [Famitsu analysis](https://www.famitsu.com/news/202106/01222293.html)
- **Hint Frequency Equations**: Derived from [Mukakin Blog research](https://www.mukakin-blog.com/491634168.html)