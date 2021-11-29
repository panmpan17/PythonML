from dataclasses import dataclass
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

            self.grounds.append(
                Ground(
                    self.screen_size[0] - 10,
                    (0, 20, (self.screen_size[1] / 2) - self.gap),
                    ((self.screen_size[1] / 2) + self.gap, 20, self.screen_size[1]),
                    ))
        
        # Check up ground and bottom ground
        for bird in self.birds:
            bird.touched = False
            if bird.position[1] - bird.collider_size < self.min_y:
                bird.touched = True
            elif bird.position[1] + bird.collider_size > self.max_y:
                bird.touched = True

        # Move ground and check collision
        remove = None
        for i, ground in enumerate(self.grounds):
            ground.x_offset += self.move_speed * delta_time
            if ground.x_offset < 0:
                remove = i

            for bird in self.birds:
                if not bird.touched:
                    bird.touched = self.AABB_vs_circle(
                        (ground.x_offset, *ground.up_ground), bird.position, bird.collider_size)
                if not bird.touched:
                    bird.touched = self.AABB_vs_circle(
                        (ground.x_offset, *ground.bottom_ground), bird.position, bird.collider_size)
        
        if remove is not None:
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
        self.touched = False
        self.velocity = 0
    
    def update(self, delta_time: float):
        self.velocity += self.Gravity * delta_time

        if InputSystem.K_SPACE:
            self.velocity = self.JumpForce
        
        self.position = (self.position[0], self.position[1] + self.velocity * delta_time)
    
    def draw(self, window: ManagedWindow):
        if self.touched:
            pygame.draw.circle(window.surface, Color.YELLOW, self.position, self.collider_size, 1)
        else:
            pygame.draw.circle(window.surface, Color.GREEN, self.position, self.collider_size, 1)


class FlappyBirdGame(ManagedWindow):
    def __init__(self) -> None:
        super().__init__((300, 500), step_update=False, tick=30)

        self.grounds = Grounds(480, 20, (300, 500), 2, 80, -100)
        self.children.append(self.grounds)

        self.bird = Bird(20, (150, 250))
        self.children.append(self.bird)
        self.grounds.birds.append(self.bird)
    
    def update(self, delta_time: float):
        if self.bird.touched:
            self.bird.position = (150, 250)
            self.bird.velocity = 0

            self.grounds.spawn_interval_timer = self.grounds.spawn_interval - 1
            self.grounds.grounds.clear()
