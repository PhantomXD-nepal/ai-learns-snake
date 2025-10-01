import pygame
import random
from enum import Enum
from collections import namedtuple

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


class SnakeGame:
    def __init__(self) -> None:
        self.w = 640
        self.h = 480
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.reset()

    def reset(self) -> None:
        # Initial game state
        self.direction = Direction.RIGHT

        self.head = point(self.w / 2, self.h / 2)  # center of the map
        self.snake = [
            self.head,
            point(self.head.x - BLOCK_SIZE, self.head.y),
            point(self.head.x - (2 * BLOCK_SIZE), self.head.y),
        ]
        self.score = 0
        self.food = None
        self.frame_iteration = 0
        self._place_food()

    def _place_food(self) -> None:
        x = (
            random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        )  # width - blocksize // block_size le esko grid ma position dekhauxa ra *block_size garda yo coords ma janxa
        y = (
            random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        )  # same here
        self.food = point(x, y)
        # If the food spawned inside the snake itself it should respawn the food
        if self.food in self.snake:
            self._place_food()

    def _move(self, direction: Direction):
        x = self.head.x
        y = self.head.y

        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = point(x, y)

    def play_step(self):
        # This function is going to run 60 times per second!
        # 1. Collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN

        self._move(self.direction)
        self.snake.insert(
            0, self.head
        )  # Snake object ko first index i.e always the head ma pheri naya head lai insert hanne

        # Function to check for collision
        if self._is_collision():
            self.game_over = True
            return self.game_over, self.score

        # If the snake ate food
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # Update UI and clock
        self._update_ui()  # This function will be responsible for drawing food snake and the scorebar ontop!
        self.clock.tick(SPEED)
        # Return game over and score
        return self.game_over, self.score

    def draw_grid(self):
        # vertical lines
        for x in range(0, self.w, BLOCK_SIZE):
            pygame.draw.line(self.display, (40, 40, 40), (x, 0), (x, self.h))

        # horizontal lines
        for y in range(0, self.h, BLOCK_SIZE):
            pygame.draw.line(self.display, (40, 40, 40), (0, y), (self.w, y))

    def _update_ui(self):
        self.display.fill(BLACK)
        self.draw_grid()

        for point in self.snake:  # Snake ko points haru return garxa
            pygame.draw.rect(
                self.display,
                BLUE1,
                pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE),
            )
            pygame.draw.rect(
                self.display, BLUE1, pygame.Rect(point.x + 4, point.y + 4, 10, 10)
            )  # Styling

        # Draw food
        # pyright: ignore[reportOptionalMemberAccess]
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
        pygame.display.update()

    def _is_collision(self) -> bool:
        if self.head.x > self.w - BLOCK_SIZE:
            return True

        if self.head.x < 0:
            return True

        if self.head.y > self.h - BLOCK_SIZE:
            return True

        if self.head.y < 0:
            return True

        # If snake hits itself then
        if self.head in self.snake[1:]:
            return True

        return False


if __name__ == "__main__":
    game = SnakeGame()

    while True:
        game_over, score = game.play_step()

        if game_over == True:
            break

    print("Final Score: ", score)

    pygame.quit()
    quit()
