import random
from blackjack_env import BlackjackEnv
import matplotlib.pyplot as plt
import numpy as np

def train():
    env = BlackjackEnv()
    num_episodes = 500_000
    epsilon = 1.0
    epsilon_min = 0.05
    epsilon_decay = 0.999

    Q = {}
    returns_sum = {}
    returns_count = {}

    wins = 0
    win_rates = []

    for episode_num in range(num_episodes):
        state = env.reset()
        done = False
        episode = []

        while not done:
            if state not in Q:
                Q[state] = [0.0,0.0]

            #epsilon-greedy
            if random.random() < epsilon:
                action = random.choice([0,1])
            else:
                action = Q[state].index(max(Q[state]))
            
            next_state, reward, done = env.step(action)
            episode.append((state,action))
            state = next_state
        
        G = reward
        if G == 1:
            wins += 1

        visited = set()
        for state, action, in episode:
            if (state,action) not in visited:
                visited.add((state,action))

                if (state,action) not in returns_sum:
                    returns_sum[(state, action)] = 0.0
                    returns_count[(state, action)] = 0

                returns_sum[(state,action)] += G
                returns_count[((state, action))] += 1

                Q[state][action] = (returns_sum[(state,action)] / returns_count[(state,action)])

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        if (episode_num + 1) % 20_000 == 0:
            block_win_rate = wins / 20_000
            win_rates.append(block_win_rate)
            print(f"Episode {episode_num+1} | Win Rate: {block_win_rate:.4f}")
            wins = 0

    print("Training complete")
    print("Total learned states: ", len(Q))
        
    return Q, win_rates

def evaluate(Q, games = 10_000):
    env = BlackjackEnv()
    wins = 0
    for _ in range(games):
        state = env.reset()
        done = False

        while not done:
            if state in Q:
                action = Q[state].index(max(Q[state]))
            else:
                action = random.choice([0,1])

            state, reward, done = env.step(action)

        if reward == 1:
            wins += 1

    win_rate = wins/games
    print(f"Win Rate: {win_rate: .4f}")
    return win_rate

def evaluate_random(games = 10_000):
    env = BlackjackEnv()
    wins = 0

    for _ in range(games):
        state = env.reset()
        done = False

        while not done:
            action = random.choice([0, 1])
            state, reward, done = env.step(action)

        if reward == 1:
            wins += 1

    print(f"Random Win Rate: {wins/games:.4f}")

def evaluate_heuristic(games=10_000):
    env = BlackjackEnv()
    wins = 0

    for _ in range(games):
        state = env.reset()
        done = False

        while not done:
            player_total, dealer_upcard, usable = state
            action = 1 if player_total < 17 else 0
            state, reward, done = env.step(action)

        if reward == 1:
            wins += 1

    print(f"Heuristic Win Rate: {wins/games:.4f}")

def plot_learning(win_rates):
    plt.figure(figsize=(8,5))
    plt.plot(win_rates)
    plt.xlabel("20k Episode Blocks")
    plt.ylabel("Win Rate")
    plt.title("Monte-Carlo Convergence")
    plt.grid(True)
    plt.show()

def print_policy(Q):
    print("\nLearned Policy (usable_ace = False)")
    print("Dealer →   2  3  4  5  6  7  8  9 10 11")

    for player_total in range(12, 21):
        row = f"{player_total:<10}"
        for dealer in range(2, 12):
            state = (player_total, dealer, False)
            if state in Q:
                action = Q[state].index(max(Q[state]))
                symbol = "H" if action == 1 else "S"
            else:
                symbol = "-"
            row += f"{symbol:>3}"
        print(row)

def plot_heatmap(Q):
    values = np.zeros((9,10))

    for i, player_total in enumerate(range(12, 21)):
        for j, dealer in enumerate(range(2, 12)):
            state = (player_total, dealer, False)
            if state in Q:
                values[i, j] = Q[state][1] - Q[state][0]

    plt.figure(figsize=(8,6))
    plt.imshow(values, cmap="coolwarm", origin="lower")
    plt.colorbar(label="Q(Hit) - Q(Stand)")
    plt.xticks(range(10), range(2,12))
    plt.yticks(range(9), range(12,21))
    plt.xlabel("Dealer Upcard")
    plt.ylabel("Player Total")
    plt.title("Decision Surface(Monte-Carlo)")
    plt.show()


            
if __name__ == "__main__":
    Q, win_rates = train()

    import pickle
    with open("mc_policy.pkl", "wb") as f:
        pickle.dump(Q, f)

    print("\nMonte Carlo Evaluation:")
    evaluate(Q)

    print("\nBaselines:")
    evaluate_random()
    evaluate_heuristic()

    plot_learning(win_rates)
    print_policy(Q)
    plot_heatmap(Q)