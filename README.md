# Umamusume Training Simulator

A Python-based simulator for Umamusume Pretty Derby training mechanics, focusing on accurate stat growth, failure rates, and support card interactions.

## Project Structure

- `sage_sim/` - Contains an old version of the simulator (will be deleted later)
- `character.json` - Character data including base stats, growth rates, and aptitudes
- `support_cards.json` - Support card definitions with bonuses and effects
- `train.py` - Main simulator file with core classes and functions
- `support_card.py` - Support card class implementation

## API Structure

### Main Classes

#### `Uma`
The primary character class that handles all training mechanics.

**Key Methods:**
- `__init__(character_data, support_cards)` - Initialize character with data and support cards
- `train(training_type, current_turn=None)` - Execute training with failure/success logic
- `rest()` - Rest action with energy recovery probabilities
- `recreation()` - Recreation activities (karaoke, stroll, shrine visits)
- `infirmary()` - Remove bad conditions and recover energy
- `rest_and_recreation()` - Combined rest/recreation for summer turns
- `get_training_stats(training_type)` - Calculate stat gains for training
- `assign_supports()` - Randomly assign support cards to facilities
- `displayStats()` - Show current character state
- `turn()` - Execute a single turn of training

#### `support`
Support card class with training bonuses and effects.

**Key Methods:**
- `get_weight()` - Calculate facility assignment probabilities
- `get_mood_eff()` - Mood effectiveness multiplier
- `get_train_eff()` - Training effectiveness multiplier  
- `get_friend_eff()` - Friendship bonus multiplier

### Key Functions

- `load_character(character_name)` - Load character data from JSON
- `load_support_card(name)` - Load individual support card by name
- `calculate_failure_rate(training_type, energy_after_training)` - Compute training failure probability
- `sim_training_fail(training_type, energy_after_training)` - Simulate training failure
- `get_training_level(clicks)` - Convert facility clicks to training level

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
- $M$ = Mood multiplier: $1 + (\text{mood} - 2) \cdot 0.1 \cdot \text{mood\\_effect}$
- $T$ = Training effectiveness: $1 + \text{training\\_eff}/100$
- $P$ = Partner bonus: $1 + 0.05 \cdot \text{num\\_partners}$
- $\text{Fr}$ = Friend bonus: $1 + \text{friendship\\_bonus}/100$ (when bond ≥ 80)

### Support Card Assignment
Support cards are assigned to facilities each turn based on weighted probabilities:

$$P_{\text{facility}} = \begin{cases}
0.18 \cdot (1 + \text{specialty\\_priority}/100) & \text{if specialty facility} \\
0.18 - \frac{\text{specialty\\_bonus}}{4} & \text{if other facility} \\
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

### Racing System
- Race participation and results
- Racing rewards (fans, skill points, money)
- Race-specific stat requirements and performance calculations
- Seasonal race schedules and G1/G2/G3 classifications

### Random Events
- Support card events and story branches
- Trainee random events and interactions
- Special training events (hot springs, etc.)
- Seasonal events and festivals

### Advanced Mechanics
- **Legacy System**: Inheritance of stats and skills from previous generations
- **Sparks**: Temporary stat boosts during training
- **Skill System**: Learning and upgrading racing skills
- **Conditions**: Additional status effects beyond basic good/bad conditions
- **Scenario-Specific Mechanics**: URA, Aoharu, MANT, etc.

### Support Card Features
- Support card events and branching dialogues
- Hint system for skill acquisition
- Support card-specific training bonuses
- Rainbow spark and other special effects

### Character Progression
- Awakening levels and stat caps
- Factor inheritance system  
- Multiple scenario routes and endings
- Character-specific unique skills and events

## Data Sources

- **Failure Rate Curves**: Fitted from energy sampling data from JP server gameplay
- **Probability Distributions**: Based on samples from [Famitsu analysis](https://www.famitsu.com/news/202106/01222293.html)
- **Hint Frequency Equations**: Derived from [Mukakin Blog research](https://www.mukakin-blog.com/491634168.html)
