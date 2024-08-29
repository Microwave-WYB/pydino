import pygame
import pygame.gfxdraw
from pygame.sprite import Sprite, WeakSprite

from reactgame.state import MutableState

pygame.init()  # Initialize all pygame modules
pygame.font.init()  # Explicitly initialize the font module

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800


class Player(Sprite):
    def __init__(self, x: int, y: int, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.image = pygame.Surface((50, 50))
        self.image.fill("red")
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(bottomleft=(x, WINDOW_HEIGHT - y))
        self.speed_y = MutableState[int](0)
        self.speed_y.notify(self.move)

    def move(self, speed_y: int) -> None:
        new_y = min(WINDOW_HEIGHT, max(50, self.rect.bottom - speed_y))
        self.rect.bottom = new_y

    def jump(self):
        self.speed_y.set(15)

    def update(self, dt: float) -> None:
        self.speed_y.set(self.speed_y.get() - 1)

    def draw(self) -> None:
        self.surface.blit(self.image, self.rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.jump()


class Obstacle(WeakSprite):
    def __init__(self, x: int, y: int, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.image = pygame.Surface((10, 30))
        self.image.fill("black")
        self.rect = self.image.get_rect(bottomleft=(x, WINDOW_HEIGHT - y))
        self.speed_x = MutableState[int](-5)

    def update(self, dt: float):
        self.rect.x += self.speed_x.get()

    def draw(self):
        self.surface.blit(self.image, self.rect)

    def handle_events(self, events: list[pygame.event.Event]): ...


class Background(Sprite):
    def __init__(self, x: int, y: int, surface: pygame.Surface):
        super().__init__()
        self.surface = surface

    def draw(self):
        self.surface.fill("white")

    def handle_events(self, events: list[pygame.event.Event]): ...


class Score(Sprite):
    def __init__(self, x: int, y: int, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.score = 0
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, 36)  # Default font, size 36

    def draw(self):
        score_text = self.font.render(
            f"Score: {self.score}", True, (0, 0, 0)
        )  # Changed to black text
        self.surface.blit(score_text, (self.x, self.y))

    def set(self, score: int):
        self.score = score

    def get(self) -> int:
        return self.score


class GameModel:
    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.player = Player(100, 0, surface)  # 50 pixels above the bottom
        self.obstacles = [Obstacle(800, 0, surface)]  # 30 pixels above the bottom
        self.background = Background(0, 0, surface)
        self.score = Score(10, 10, surface)
        self.pass_flag = False

    def check_pass(self) -> None:
        if self.pass_flag:
            return
        else:
            if self.player.rect.right > self.obstacles[0].rect.right:
                self.pass_flag = True
                self.score.set(self.score.get() + 1)

    def game_over(self) -> None:
        self.score.set(0)
        self.player.rect.bottom = WINDOW_HEIGHT
        self.obstacles[0].rect.right = 800

    def check_collision(self) -> None:
        for obstacle in self.obstacles:
            if self.player.rect.colliderect(obstacle.rect):
                self.game_over()

    def check_obstacle_out_of_screen(self):
        if self.obstacles[0].rect.right < 0:
            self.obstacles.remove(self.obstacles[0])
            self.obstacles.append(Obstacle(800, 0, self.surface))
            self.pass_flag = False

    def add_obstacle(self):
        self.obstacles.append(Obstacle(800, 0, self.surface))

    def remove_obstacle(self):
        self.obstacles.remove(self.obstacles[0])

    def update(self, dt: float):
        self.player.update(dt)
        self.score.update(dt)
        for obstacle in self.obstacles:
            obstacle.update(dt)
            self.check_pass()
            self.check_obstacle_out_of_screen()
            self.check_collision()

    def draw(self):
        self.background.draw()
        self.player.draw()
        for obstacle in self.obstacles:
            obstacle.draw()
        self.score.draw()

    def handle_events(self, events: list[pygame.event.Event]):
        self.player.handle_events(events)
        for obstacle in self.obstacles:
            obstacle.handle_events(events)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.model = GameModel(self.screen)

    def update(self, dt: float):
        self.model.update(dt)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        self.model.handle_events(events)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            events = pygame.event.get()
            self.handle_events(events)
            self.update(dt)
            self.model.draw()
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
