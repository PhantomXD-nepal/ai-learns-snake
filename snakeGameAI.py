import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()

font = pygame.font.SysFont("arial", 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


point = namedtuple("Point", "x, y")

WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 10


class SnakeGameAi:
    def __init__(self) -> None:
        self.w = 640
        self.h = 480
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self) -> None:
        # Initial game state
        self.direction = Direction.RIGHT
        self.head = point(self.w / 2, self.h / 2)
        self.snake = [
            self.head,
            point(self.head.x - BLOCK_SIZE, self.head.y),
            point(self.head.x - (2 * BLOCK_SIZE), self.head.y),
        ]
        self.score = 0
        self.food = None
        self.frame_iteration = 0
        self.game_over = False  # ← CRITICAL FIX: Reset game_over flag
        self._place_food()

    def _place_food(self) -> None:
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = point(x, y)
        if self.food in self.snake:
            self._place_food()

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index_of_current_direction = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):  # Straight
            new_dir = clock_wise[index_of_current_direction]
        elif np.array_equal(action, [0, 1, 0]):  # Right turn
            next_index = (index_of_current_direction + 1) % 4
            new_dir = clock_wise[next_index]
        else:  # [0,0,1] Left turn
            next_index = (index_of_current_direction - 1) % 4
            new_dir = clock_wise[next_index]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = point(x, y)

    def play_step(self, action):
        self.frame_iteration += 1

        # Check for quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Move snake
        self._move(action)
        self.snake.insert(0, self.head)

        # Initialize reward
        reward = 0
        game_over = False

        # Check for collision or timeout
        if self._is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return game_over, self.score, reward

        # Check if snake ate food
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()  # Remove tail if didn't eat

        # Update UI and clock
        self._update_ui()
        self.clock.tick(SPEED)

        return game_over, self.score, reward

    def draw_grid(self):
        for x in range(0, self.w, BLOCK_SIZE):
            pygame.draw.line(self.display, (40, 40, 40), (x, 0), (x, self.h))
        for y in range(0, self.h, BLOCK_SIZE):
            pygame.draw.line(self.display, (40, 40, 40), (0, y), (self.w, y))

    def _update_ui(self):
        self.display.fill(BLACK)
        self.draw_grid()

        for pt in self.snake:
            pygame.draw.rect(
                self.display,
                BLUE1,
                pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE),
            )
            pygame.draw.rect(
                self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12)
            )

        # Draw food
        pygame.draw.circle(
            self.display,
            RED,
            (
                self.food.x + BLOCK_SIZE // 2,
                self.food.y + BLOCK_SIZE // 2,
            ),
            BLOCK_SIZE // 2,
        )

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _is_collision(self, point=None) -> bool:
        if point is None:
            point = self.head

        # Check boundary collision
        if point.x > self.w - BLOCK_SIZE or point.x < 0:
            return True
        if point.y > self.h - BLOCK_SIZE or point.y < 0:
            return True

        # Check self collision
        if point in self.snake[1:]:
            return True

        return False
