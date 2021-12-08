import pygame
import sys

from typing import List, Tuple


class Color:
    WHITE = (255, 255, 255)
    ORANGE = (255, 200, 0)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    PINK = (255, 230, 230)


Vector = Tuple[int, int]
Rect = Tuple[int, int, int, int]


class Math:
    @staticmethod
    def lerp(a: float, b: float, percentage: float) -> float:
        return (b - a) * percentage + a

    @staticmethod
    def lerp_point(point_a: Vector, point_b: Vector, percentage: float) -> Vector:
        return (Math.lerp(point_a[0], point_b[0], percentage), Math.lerp(point_a[1], point_b[1], percentage))

    @staticmethod
    def magnitude(point_a: Vector, point_b: Vector=None) -> float:
        if point_b is None:
            return (point_a[0] ** 2 + point_a[1] ** 2) ** 0.5
        else:
            return ((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2) ** 0.5

    @staticmethod
    def sqr_magnitude(point_a: Vector, point_b: Vector) -> float:
        return (point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2
    
    @staticmethod
    def clamp_magnitude(vector: Vector, distance: float) -> Vector:
        magnitude = ((vector[0] ** 2 + vector[1] ** 2) ** 0.5) / distance
        return (vector[0] / magnitude, vector[1] / magnitude)

    @staticmethod
    def tuple_multiple(point_a: Vector, point_b: Vector | float) -> Vector:
        if isinstance(point_b, float) or isinstance(point_b, int):
            return (point_a[0] * point_b, point_a[1] * point_b)
        else:
            return (point_a[0] * point_b[0], point_a[1] * point_b[1])

    @staticmethod
    def tuple_plus(point_a: Vector, point_b: Vector) -> Vector:
        return (point_a[0] + point_b[0], point_a[1] + point_b[1])

    @staticmethod
    def tuple_minus(point_a: Vector, point_b: Vector) -> Vector:
        return (point_a[0] - point_b[0], point_a[1] - point_b[1])

    @staticmethod
    def normalize(vector: Vector) -> Vector:
        magnitude = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        return (vector[0] / magnitude, vector[1] / magnitude)


class InputSystem:
    MOUSE_DOWN = False
    MOUSE_UP = False
    MOUSE_POS = (0, 0)

    K_SPACE = False
    K_Z = False
    K_X = False


class Entity:
    def update(self,  delta_time: float):
        raise NotImplementedError("Draw function not implemented")

    def draw(self, window: "ManagedWindow"):
        raise NotImplementedError("Draw function not implemented")


class Point(Entity):
    def __init__(self, position, color=None, radius=3, width=2):
        self.position = position

        if color is None:
            self.color = Color.WHITE
        else:
            self.color = color
        
        self.radius = radius
        self.width = width

    def update(self, delta_time: float):
        pass

    def draw(self, window: "ManagedWindow"):
        pygame.draw.circle(window.surface, self.color, self.position, self.radius, self.width)


class ManagedWindow:
    def __init__(self, size: Vector, step_update=False, tick=30, tick_limit=True) -> None:
        self.size = size
        self.full_rect = (0, 0, *size)
        self.surface: pygame.Surface = None
        self.background_color = Color.BLACK

        self.children: List[Entity] = []

        self.step_update = step_update

        self.tick = tick
        self.tick_limit = tick_limit

    def update(self, delta_time: float):
        pass

    def run(self):
        pygame.init()

        self.surface = pygame.display.set_mode(self.size)

        clock = pygame.time.Clock()
        delta_time = 1 / self.tick

        while True:
            InputSystem.MOUSE_DOWN = False
            InputSystem.MOUSE_UP = False
            InputSystem.K_SPACE = False
            InputSystem.K_Z = False
            InputSystem.K_X = False
            update_key_pressed = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    InputSystem.MOUSE_DOWN = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    InputSystem.MOUSE_UP = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        InputSystem.K_SPACE = True
                    elif event.key == pygame.K_x:
                        InputSystem.K_X = True
                    elif event.key == pygame.K_z:
                        InputSystem.K_Z = True
                    elif event.key == pygame.K_LSHIFT:
                        update_key_pressed = True
                    elif event.key == pygame.K_RETURN:
                        self.step_update = not self.step_update

            InputSystem.MOUSE_POS = pygame.mouse.get_pos()
            
            pygame.draw.rect(self.surface, self.background_color, self.full_rect)

            for child in self.children:
                if self.step_update:
                    if update_key_pressed:
                        child.update(1 / 30)
                else:
                    child.update(delta_time)

                child.draw(self)

            self.update(delta_time)

            pygame.display.flip()

            if self.tick_limit:
                clock.tick(self.tick)

