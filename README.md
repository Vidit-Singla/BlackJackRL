# BlackjackRL 

A reinforcement learning agent trained to play Blackjack using **Monte Carlo Control**, built from scratch with a custom environment and a full pygame visualization.

The agent converges to a **47.6% win rate** — matching optimal basic strategy — while a random policy only achieves ~23%.

---

## Demo

The trained policy is loaded into a pygame simulation where the AI plays autonomously, making hit/stand decisions in real time.

> `blackjack_ai_demo.py` — runs the AI demo  
> `blackjack.py` — play it yourself

---

## Results

| Agent | Win Rate |
|---|---|
| Random policy | ~23% |
| Heuristic (hit < 17) | ~46.7% |
| **Monte Carlo (trained)** | **47.6%** |

Trained over **500,000 episodes** with ε-greedy exploration (ε decayed from 1.0 → 0.05).  
The agent converges by ~episode 80,000 and discovers a policy consistent with known optimal Blackjack strategy.

---

## How It Works

### Environment (`blackjack_env.py`)
A custom Blackjack environment built from scratch (no external RL libraries). The state space is:

```
(player_total, dealer_upcard, usable_ace)
```

Actions: `0 = Stand`, `1 = Hit`  
Rewards: `+1` win, `0` draw, `-1` loss

### Algorithm (`train_montecarlo.py`)
**First-visit Monte Carlo Control** with ε-greedy exploration.

Monte Carlo is well-suited to Blackjack because:
- Episodes are short and naturally terminated
- Rewards are only available at the end of each hand
- No bootstrapping needed — full returns are used directly

The Q-table converges to **280 unique states**, matching the theoretical state space of the game.

---

## Project Structure

```
BlackjackRL/
├── blackjack_env.py       # Custom Blackjack RL environment
├── train_montecarlo.py    # Monte Carlo training + evaluation
├── blackjack_ai_demo.py   # Pygame AI demo (loads trained policy)
├── blackjack.py           # Playable Blackjack game
├── mc_policy.pkl          # Saved trained Q-table
└── assets/                # Card images and table graphics
```


---

## Getting Started

```bash
git clone https://github.com/vidit-singla/BlackjackRL.git
cd BlackjackRL
pip install -r requirements.txt
```

**Train the agent:**
```bash
python train_montecarlo.py
```

**Watch the AI play:**
```bash
python blackjack_ai_demo.py
```

**Play yourself:**
```bash
python blackjack.py
# H = Hit, S = Stand, R = New round
```

---


