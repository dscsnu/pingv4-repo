"""
Connect4 using AI/ML (I think)
Neural Network AI that learns to play through self-play and reinforcement learning.
Solely uses NumPy - no external ML libraries required.
"""

import numpy as np
import random
import pickle
from typing import List, Tuple, Optional


class Connect4:
    """Connect4 game logic."""

    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.reset()

    def reset(self):
        """Reset the game board."""
        self.board = np.zeros((self.rows, self.cols), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        return self.get_state()

    def get_state(self):
        """Get current board state."""
        return self.board.copy()

    def get_valid_moves(self):
        """Return list of valid column indices."""
        return [col for col in range(self.cols) if self.board[0][col] == 0]

    def drop_piece(self, col):
        """Drop a piece in the specified column."""
        if col not in self.get_valid_moves():
            return False, self.get_state(), 0

        # Find the lowest empty row
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.current_player
                break

        # Check for win
        reward = 0
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
            reward = 2  # Win reward
        elif len(self.get_valid_moves()) == 0:
            self.game_over = True
            self.winner = 0  # Draw
            reward = 1
        else:
            # Switch players
            self.current_player = 3 - self.current_player  # Toggle between 1 and 2

        return True, self.get_state(), reward

    def check_win(self, row, col):
        """Check if the last move resulted in a win."""
        piece = self.board[row][col]

        # Check all directions
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for delta_row, delta_col in directions:
            count = 1
            # Check positive direction
            count += self._count_consecutive(row, col, delta_row, delta_col, piece)
            # Check negative direction
            count += self._count_consecutive(row, col, -delta_row, -delta_col, piece)

            if count >= 4:
                return True

        return False

    def _count_consecutive(self, row, col, delta_row, delta_col, piece):
        """Count consecutive pieces in a direction."""
        count = 0
        r, c = row + delta_row, col + delta_col

        while (0 <= r < self.rows and
               0 <= c < self.cols and
               self.board[r][c] == piece):
            count += 1
            r += delta_row
            c += delta_col

        return count

    def display_board(self):
        """Display the current board."""
        symbols = {0: '.', 1: 'X', 2: 'O'}
        print("\n  " + " ".join(str(i) for i in range(self.cols)))
        for row in self.board:
            print("  " + " ".join(symbols[cell] for cell in row))
        print()


class NeuralNetwork:
    """Simple neural network for Connect4 AI."""

    def __init__(self, input_size=42, hidden_size=128, output_size=7):
        """Initialize network with random weights."""
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Xavier initialization
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2.0 / input_size)
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, hidden_size) * np.sqrt(2.0 / hidden_size)
        self.b2 = np.zeros(hidden_size)
        self.W3 = np.random.randn(hidden_size, output_size) * np.sqrt(2.0 / hidden_size)
        self.b3 = np.zeros(output_size)

    def relu(self, x):
        """ReLU activation function."""
        return np.maximum(0, x)

    def relu_derivative(self, x):
        """Derivative of ReLU."""
        return (x > 0).astype(float)

    def forward(self, x):
        """Forward pass through the network."""
        self.z1 = np.dot(x, self.W1) + self.b1
        self.a1 = self.relu(self.z1)

        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.relu(self.z2)

        self.z3 = np.dot(self.a2, self.W3) + self.b3
        self.output = self.z3

        return self.output

    def predict(self, state):
        """Predict action values for a given state."""
        # Flatten board and normalize
        x = state.flatten() / 2.0  # Normalize to [0, 1]
        return self.forward(x)

    def save(self, filename):
        """Save network weights."""
        weights = {
            'W1': self.W1, 'b1': self.b1,
            'W2': self.W2, 'b2': self.b2,
            'W3': self.W3, 'b3': self.b3
        }
        with open(filename, 'wb') as f:
            pickle.dump(weights, f)

    def load(self, filename):
        """Load network weights."""
        with open(filename, 'rb') as f:
            weights = pickle.load(f)
        self.W1 = weights['W1']
        self.b1 = weights['b1']
        self.W2 = weights['W2']
        self.b2 = weights['b2']
        self.W3 = weights['W3']
        self.b3 = weights['b3']


class Connect4Agent:
    """Reinforcement Learning agent for Connect4."""

    def __init__(self, epsilon=0.1, learning_rate=0.001):
        self.network = NeuralNetwork()
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.experience_replay = []
        self.max_replay_size = 10000

    def get_action(self, state, valid_moves, training=True):
        """Choose action using epsilon-greedy policy."""
        if training and random.random() < self.epsilon:
            # Exploration: random valid move
            return random.choice(valid_moves)
        else:
            # Exploitation: best predicted move
            q_values = self.network.predict(state)

            # Mask invalid moves
            masked_q_values = np.full(7, -np.inf)
            masked_q_values[valid_moves] = q_values[valid_moves]

            return np.argmax(masked_q_values)

    def store_experience(self, state, action, reward, next_state, done):
        """Store experience for replay."""
        self.experience_replay.append((state, action, reward, next_state, done))

        if len(self.experience_replay) > self.max_replay_size:
            self.experience_replay.pop(0)

    def train_on_batch(self, batch_size=32, gamma=0.95):
        """Train on a batch of experiences using Q-learning."""
        if len(self.experience_replay) < batch_size:
            return

        # Sample random batch
        batch = random.sample(self.experience_replay, batch_size)

        for state, action, reward, next_state, done in batch:
            # Current Q-values
            current_q = self.network.predict(state)

            if done:
                target_q = reward
            else:
                # Q-learning: max Q-value of next state
                next_q = self.network.predict(next_state)
                target_q = reward + gamma * np.max(next_q)

            # Update target for the action taken
            target = current_q.copy()
            target[action] = target_q

            # Gradient descent (simplified)
            self._gradient_update(state, target)

    def _gradient_update(self, state, target):
        """Perform gradient descent update."""
        x = state.flatten() / 2.0

        # Forward pass
        prediction = self.network.forward(x)

        # Compute loss and gradients (MSE)
        error = prediction - target

        # Backward pass (backpropagation)
        dW3 = np.outer(self.network.a2, error)
        db3 = error

        da2 = np.dot(error, self.network.W3.T)
        dz2 = da2 * self.network.relu_derivative(self.network.z2)
        dW2 = np.outer(self.network.a1, dz2)
        db2 = dz2

        da1 = np.dot(dz2, self.network.W2.T)
        dz1 = da1 * self.network.relu_derivative(self.network.z1)
        dW1 = np.outer(x, dz1)
        db1 = dz1

        # Update weights
        self.network.W3 -= self.learning_rate * dW3
        self.network.b3 -= self.learning_rate * db3
        self.network.W2 -= self.learning_rate * dW2
        self.network.b2 -= self.learning_rate * db2
        self.network.W1 -= self.learning_rate * dW1
        self.network.b1 -= self.learning_rate * db1

    def save(self, filename):
        """Save agent."""
        self.network.save(filename)

    def load(self, filename):
        """Load agent."""
        self.network.load(filename)


def train_agent(episodes=1000, save_path='connect4_ai.pkl'):
    """Train the AI through self-play."""
    agent1 = Connect4Agent(epsilon=0.2, learning_rate=0.001)
    agent2 = Connect4Agent(epsilon=0.2, learning_rate=0.001)

    wins = {1: 0, 2: 0, 0: 0}  # Player 1, Player 2, Draws

    print("Training Connect4 AI through self-play...")

    for episode in range(episodes):
        game = Connect4()
        state = game.reset()

        while not game.game_over:
            valid_moves = game.get_valid_moves()

            if game.current_player == 1:
                action = agent1.get_action(state, valid_moves, training=True)
                current_agent = agent1
            else:
                action = agent2.get_action(state, valid_moves, training=True)
                current_agent = agent2

            success, next_state, reward = game.drop_piece(action)

            if not success:
                continue

            # Store experience
            done = game.game_over
            if done and game.winner == game.current_player:
                # The OTHER player just won (we switched already)
                reward = -1
            elif done and game.winner == 0:
                reward = 0.5
            else:
                reward = 0

            current_agent.store_experience(state, action, reward, next_state, done)

            state = next_state

        # Record winner
        if game.winner is not None:
            wins[game.winner] += 1

        # Train both agents
        agent1.train_on_batch(batch_size=32)
        agent2.train_on_batch(batch_size=32)

        # Decay epsilon
        agent1.epsilon = max(0.01, agent1.epsilon * 0.995)
        agent2.epsilon = max(0.01, agent2.epsilon * 0.995)

        # Progress update
        if (episode + 1) % 100 == 0:
            print(f"Episode {episode + 1}/{episodes}")
            print(f"  Wins - P1: {wins[1]}, P2: {wins[2]}, Draws: {wins[0]}")
            print(f"  Epsilon: {agent1.epsilon:.3f}")
            wins = {1: 0, 2: 0, 0: 0}

    # Save the trained agent
    agent1.save(save_path)
    print(f"\nTraining complete! AI saved to {save_path}")

    return agent1


def play_against_ai(agent_path='connect4_ai.pkl'):
    """Play against the trained AI."""
    agent = Connect4Agent(epsilon=0.0)  # No exploration during play

    try:
        agent.load(agent_path)
        print("AI loaded successfully!")
    except FileNotFoundError:
        print("No trained AI found. Training a new one...")
        agent = train_agent(episodes=500, save_path=agent_path)

    game = Connect4()
    game.reset()

    print("\nWelcome to Connect4 vs AI!")
    print("You are X (Player 1), AI is O (Player 2)")

    while not game.game_over:
        game.display_board()

        if game.current_player == 1:
            # Human's turn
            valid_moves = game.get_valid_moves()
            print(f"Valid moves: {valid_moves}")

            try:
                col = int(input("Your move (column 0-6): "))
                if col not in valid_moves:
                    print("Invalid move! Try again.")
                    continue
            except ValueError:
                print("Please enter a number!")
                continue
        else:
            # AI's turn
            state = game.get_state()
            valid_moves = game.get_valid_moves()
            col = agent.get_action(state, valid_moves, training=False)
            print(f"AI plays column {col}")

        game.drop_piece(col)

    game.display_board()

    if game.winner == 1:
        print("🎉 You win! 🎉")
    elif game.winner == 2:
        print("🤖 AI wins! 🤖")
    else:
        print("It's a draw!")


if __name__ == "__main__":
    import sys

    print("Connect4 with Machine Learning")
    print("=" * 50)
    print("1. Train new AI")
    print("2. Play against AI")
    print("3. Watch AI self-play")

    choice = input("\nChoose option (1-3): ").strip()

    if choice == "1":
        episodes = int(input("Number of training episodes (default 1000): ") or "1000")
        train_agent(episodes=episodes)
    elif choice == "2":
        play_against_ai()
    elif choice == "3":
        # Quick training for demo
        print("\nTraining AI briefly for demonstration...")
        agent = train_agent(episodes=200)

        # Watch self-play
        print("\nWatching AI play against itself...")
        game = Connect4()
        game.reset()

        while not game.game_over:
            game.display_board()
            state = game.get_state()
            valid_moves = game.get_valid_moves()
            col = agent.get_action(state, valid_moves, training=False)
            print(f"Player {game.current_player} plays column {col}")
            game.drop_piece(col)
            input("Press Enter to continue...")

        game.display_board()
        print(f"Game over! Winner: Player {game.winner if game.winner else 'Draw'}")
    else:
        print("Invalid choice!")
