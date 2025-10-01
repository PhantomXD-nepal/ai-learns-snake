import torch
import random
import numpy as np
from snakeGameAI import SnakeGameAi, Direction, point
from collections import deque

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self) -> None:
        self.n_games = 0
        self.epsilon = 0  # Randomness calculator
        self.gamma = 0  # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()

        # TODO: model and trainer

    def get_state(self, game):
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
            (dir_d and game.is_collision(point_r))
            or (dir_u and game.is_collision(point_l))
            or (dir_r and game.is_collision(point_u))
            or (dir_l and game.is_collision(point_d)),
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
        

    def train_long_memory(self):
        pass

    def train_short_memory(self, state, action, reward, next_state, done):
        pass

    def get_action(self, state):
        pass


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
        reward, done, score = game.play_step(final_move)
        new_state = agent.get_state(game)

        # Train short memory
        agent.train_short_memory(state_old, final_move, reward, new_state, done)

        # Remember
        agent.remember(state_old, final_move, reward, new_state, done)

        if done:
            # Train long memory
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                # agent.model.save()
            print("Game:", agent.n_games, "Score:", score, "Record:", record)

            # TODO: Plot scores


if __name__ == "__main__":
    train()
