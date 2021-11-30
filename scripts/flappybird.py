import random
import time
import json

from dataclasses import dataclass
from scripts.NEAT import Genome, genome_feed_data, connection_weight_random_add
from .pygame_foundation import *


@dataclass
class Ground:
    x_offset:float
    up_ground: Tuple[float, float, float]
    bottom_ground: Tuple[float, float, float]


class Grounds(Entity):
    @staticmethod
    def AABB_vs_circle(aabb:Rect, center:Vector, radius) -> bool:
        if center[0] + radius < aabb[0]:
            return False
        if center[0] - radius > (aabb[0] + aabb[2]):
            return False
        if center[1] + radius < aabb[1]:
            return False
        if center[1] - radius > (aabb[1] + aabb[3]):
            return False

        return True

    def __init__(self, max_y, min_y, screen_size, spawn_interval, gap, move_speed) -> None:
        self.max_y = max_y
        self.min_y = min_y
        self.screen_size = screen_size

        self.spawn_interval = spawn_interval
        self.spawn_interval_timer = spawn_interval - 1
        self.gap = gap
        self.grounds: List[Ground] = []

        self.move_speed = move_speed
        self.birds: List["Bird"] = []

    def update(self, delta_time: float):
        self.spawn_interval_timer += delta_time
        if self.spawn_interval_timer > self.spawn_interval:
            self.spawn_interval_timer = 0

            y = (self.screen_size[1] / 2) + random.randint(-150, 150)

            self.grounds.append(
                Ground(
                    self.screen_size[0] - 10,
                    (0, 30, y - self.gap),
                    (y + self.gap, 30, self.screen_size[1]),
                    ))
        
        # Check up ground and bottom ground
        for bird in self.birds:
            if bird.alive:
                if bird.position[1] - bird.collider_size < self.min_y:
                    bird.kill()
                elif bird.position[1] + bird.collider_size > self.max_y:
                    bird.kill()

        # Move ground and check collision
        remove = None
        for i, ground in enumerate(self.grounds):
            ground.x_offset += self.move_speed * delta_time
            if ground.x_offset < 0:
                remove = i

            for bird in self.birds:
                if bird.alive:
                    if self.AABB_vs_circle((ground.x_offset,
                                            *ground.up_ground),
                                           bird.position, bird.collider_size):
                        bird.kill()
                if bird.alive:
                    if self.AABB_vs_circle((ground.x_offset,
                                            *ground.bottom_ground),
                                           bird.position, bird.collider_size):
                        bird.kill()
        
        if remove is not None:
            FlappyBirdGame.Score += 1
            self.grounds.pop(remove)

    def draw(self, window: ManagedWindow):
        pygame.draw.line(window.surface, Color.GREEN, (0, self.min_y), (self.screen_size[0], self.min_y))
        pygame.draw.line(window.surface, Color.GREEN, (0, self.max_y), (self.screen_size[0], self.max_y))

        for ground in self.grounds:
            pygame.draw.rect(window.surface, Color.GREEN, (ground.x_offset, *ground.up_ground), 1)
            pygame.draw.rect(window.surface, Color.GREEN, (ground.x_offset, *ground.bottom_ground), 1)


class Bird(Entity):
    Gravity = 400
    JumpForce = -200

    def __init__(self, collider_size:int, position:Vector) -> None:
        self.position = position
        self.collider_size = collider_size

        self.alive = True
        self.velocity = 0
    
    def kill(self) -> None:
        self.alive = False

    def update(self, delta_time: float):
        if not self.alive:
            return

        self.velocity += self.Gravity * delta_time

        if InputSystem.K_SPACE:
            self.velocity = self.JumpForce
        
        self.position = (self.position[0], self.position[1] + self.velocity * delta_time)
    
    def draw(self, window: ManagedWindow):
        if self.alive:
            # pygame.draw.circle(window.surface, Color.YELLOW, self.position, self.collider_size, 1)
            pygame.draw.circle(window.surface, Color.GREEN, self.position, self.collider_size, 1)


class GenomeBird(Bird):
    def __init__(self, genome:Genome, collider_size: int, position: Vector) -> None:
        super().__init__(collider_size, position)
        self.genome = genome
        self.score = 0
    
    def kill(self) -> None:
        super().kill()
        self.score = time.time()

    def update(self, delta_time: float):
        self.velocity += self.Gravity * delta_time

        results = genome_feed_data(genome=self.genome, inputs=[
            # self.position[0],
            self.position[1],
            # self.collider_size,
            FlappyBirdGame.UpGroundY,
            FlappyBirdGame.BottomGroundY,
        ])
        if results[0] > 0:
            self.velocity = self.JumpForce
        
        self.position = (self.position[0], self.position[1] + self.velocity * delta_time)


class FlappyBirdGame(ManagedWindow):
    UpGroundY = 0
    BottomGroundY = 0
    Score = 0

    def __init__(self, pygame_running) -> None:
        super().__init__((300, 500), step_update=False, tick=30)

        self.grounds = Grounds(480, 20, (300, 500), 2.5, 80, -100)
        self.children.append(self.grounds)

        self.birds: List[GenomeBird] = []
        self.grounds.birds = self.birds

        self.pygame_running = pygame_running

    def update(self, delta_time: float):
        if len(self.grounds.grounds) == 0:
            FlappyBirdGame.UpGroundY = 200
            FlappyBirdGame.BottomGroundY = 300
        else:
            FlappyBirdGame.UpGroundY = self.grounds.grounds[0].up_ground[0] + self.grounds.grounds[0].up_ground[2]
            FlappyBirdGame.BottomGroundY = self.grounds.grounds[0].bottom_ground[0]

        all_dead = True
        for bird in self.birds:
            if bird.alive:
                bird.update(delta_time)

                if self.pygame_running:
                    bird.draw(self)
                all_dead = False

        if all_dead:
            self.reset()
        
        if self.Score > 1000:
            for bird in self.birds:
                if bird.alive:
                    with open("result.json", "w") as f:
                        json.dump(bird.genome, f, default=lambda obj: obj.toJSON(), indent=4)

                    if self.pygame_running:
                        pygame.quit()
                    sys.exit()
                    break

    def reset(self):
        best_birds = sorted(self.birds, key=lambda bird: bird.score, reverse=True)[:10]

        self.birds.clear()

        for bird in best_birds:
            variants = connection_weight_random_add(bird.genome, 40, -4, 4)
            for variant in variants:
                bird = GenomeBird(variant, 20, (80, 250))
                bird.position = (80, 250)
                bird.velocity = 0
                self.birds.append(bird)

        self.grounds.spawn_interval_timer = self.grounds.spawn_interval - 1
        self.grounds.grounds.clear()

    def run_without_pygame(self):
        delta_time = 1 / self.tick

        while True:
            for child in self.children:
                child.update(delta_time)
            
            self.update(delta_time)
