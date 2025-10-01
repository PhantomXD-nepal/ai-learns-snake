import torch
import random
import numpy as np
from snakeGameAI import SnakeGameAi, Direction, point
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self) -> None:
        self.n_games = 0
        self.epsilon = 0  # Randomness calculator
        self.gamma = 0.82  # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()

        self.model = Linear_QNet(11, 512, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game: SnakeGameAi):
        head = game.snake[0]
        point_l = point(head.x - 20, head.y)
        point_r = point(head.x + 20, head.y)
        point_u = point(head.x, head.y - 20)
        point_d = point(head.x, head.y + 20)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game._is_collision(point_r))
            or (dir_l and game._is_collision(point_l))
            or (dir_u and game._is_collision(point_u))
            or (dir_d and game._is_collision(point_d)),
            # Danger right
            (dir_u and game._is_collision(point_r))
            or (dir_d and game._is_collision(point_l))
            or (dir_l and game._is_collision(point_u))
            or (dir_r and game._is_collision(point_d)),
            # Danger left
            (dir_d and game._is_collision(point_r))
            or (dir_u and game._is_collision(point_l))
            or (dir_r and game._is_collision(point_u))
            or (dir_l and game._is_collision(point_d)),
            # Current direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            # Food direction
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y,  # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # IMPROVED: Epsilon now stays non-negative
        self.epsilon = max(0, 80 - self.n_games)
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = int(torch.argmax(prediction).item())
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_avg_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAi()

    while True:
        # Get old state
        state_old = agent.get_state(game)

        # Get move
        final_move = agent.get_action(state_old)

        # Perform move and get new state
        # FIXED: Correct return order from play_step
        done, score, reward = game.play_step(final_move)
        new_state = agent.get_state(game)

        # Train short memory
        agent.train_short_memory(state_old, final_move, reward, new_state, done)

        # Remember
        agent.remember(state_old, final_move, reward, new_state, done)

        if done:
            # Train long memory and reset
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()
            print("Game:", agent.n_games, "Score:", score, "Record:", record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_avg_scores.append(mean_score)
            plot(plot_scores, plot_avg_scores)


if __name__ == "__main__":
    train()
