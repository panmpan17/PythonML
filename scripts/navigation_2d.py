import pygame
import math

from dataclasses import dataclass
from typing import List, Tuple
from scripts.pygame_foundation import Color, Entity, InputSystem, KeyCode, ManagedWindow, Math, Vector


class HitType:
    Nothing = 0
    Wall = 1
    Food = 2


@dataclass
class RaycastData:
    direction: Vector
    hit_point: Vector
    hit_type: HitType
    distance: float


@dataclass
class Wall:
    start_pos: Vector
    end_pos: Vector


@dataclass
class Food:
    position: Vector
    radius: float


class Character(Entity):
    def __init__(self, position:Vector, move_speed) -> None:
        super().__init__()

        self.rotation_speed = 0.1
        self.move_speed = move_speed
        self.position: Vector = position

        self._rotation = 0
        self.direction: Vector = (math.cos(0), math.sin(0))
        self.raycasts: List[RaycastData] = []

        self.radius = 10

        self.game: NavigationGame = None

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.direction = (math.cos(value), math.sin(value))
        self.recalculate_raycasts()

    def recalculate_raycasts(self):
        self.raycasts.clear()
        for rotation_delta in range(-45, 45 + 1, 5):
        # if True:
            # rotation_delta = 0
            angle = self._rotation + (rotation_delta / 60)
            direction = (math.cos(angle), math.sin(angle))

            type_, hit_point  = self.game.raycast(self.position, direction)

            self.raycasts.append(RaycastData(
                direction,
                hit_point,
                type_,
                Math.magnitude(self.position, hit_point)))

    def update(self, delta_time: float):
        direction_changes = 0
        if InputSystem.check_key_pressed(KeyCode.A):
            direction_changes -= 1
        if InputSystem.check_key_pressed(KeyCode.D):
            direction_changes += 1
        
        if direction_changes != 0:
            self.rotation += direction_changes * self.rotation_speed * delta_time

        if InputSystem.check_key_pressed(KeyCode.W):
            self.position = (self.position[0] + (self.direction[0] * self.move_speed * delta_time),
                            self.position[1] + (self.direction[1] * self.move_speed * delta_time))
            self.recalculate_raycasts()
    
    def draw(self, window: ManagedWindow):
        pygame.draw.circle(window.surface, Color.GREEN, self.position, self.radius, 2)
        # pygame.draw.line(window.surface, Color.YELLOW, self.position,
        #                  Math.tuple_plus(self.position, Math.tuple_multiple(self.direction, 40)))

        for raycast in self.raycasts:
            if raycast.hit_type == HitType.Nothing:
                pygame.draw.line(window.surface, Color.GRAY, self.position, raycast.hit_point)
            elif raycast.hit_type == HitType.Wall:
                pygame.draw.line(window.surface, Color.GREEN, self.position, raycast.hit_point)
            elif raycast.hit_type == HitType.Food:
                pygame.draw.line(window.surface, Color.YELLOW, self.position, raycast.hit_point)


class NavigationGame(ManagedWindow):
    def __init__(self, tick_limit=False) -> None:
        super().__init__((400, 400), step_update=False, tick=30, tick_limit=tick_limit)
        self.min_x = 10
        self.max_x = 390
        self.min_y = 10
        self.max_y = 390

        self.characters: List[Character] = []
        self.walls: List[Wall] = []
        self.foods: List[Food] = []

        self.walls.append(Wall((40, 60), (100, 90)))
        self.walls.append(Wall((100, 300), (150, 400)))

        self.foods.append(Food((150, 250), 5))

    def add_character(self, character: Character):
        self.characters.append(character)
        character.game = self
        character.recalculate_raycasts()

    def raycast(self, position:Vector, direction:Vector, max_distance=100) -> Tuple[HitType, Vector]:
        # normal = Math.normalize(direction)
        for _ in range(max_distance):
            position = Math.tuple_plus(position, direction)
            if position[0] <= self.min_x:
                return HitType.Wall, position
            if position[1] <= self.min_y:
                return HitType.Wall, position
            if position[0] >= self.max_x:
                return HitType.Wall, position
            if position[1] >= self.max_y:
                return HitType.Wall, position

            for wall in self.walls:
                if wall.end_pos[0] > position[0] > wall.start_pos[0]:
                    if wall.end_pos[1] > position[1] > wall.start_pos[1]:
                        return HitType.Wall, position

            for food in self.foods:
                if Math.sqr_magnitude(position, food.position) <= food.radius * food.radius:
                    return HitType.Food, position

        return HitType.Nothing, position

    def update(self, delta_time: float):
        pygame.draw.line(self.surface, Color.GREEN, (self.min_x, self.min_y), (self.min_x, self.max_y))
        pygame.draw.line(self.surface, Color.GREEN, (self.min_x, self.max_y), (self.max_x, self.max_y))
        pygame.draw.line(self.surface, Color.GREEN, (self.max_x, self.max_y), (self.max_x, self.min_y))
        pygame.draw.line(self.surface, Color.GREEN, (self.max_x, self.min_y), (self.min_x, self.min_y))

        for wall in self.walls:
            rect = (*wall.start_pos, wall.end_pos[0] - wall.start_pos[0], wall.end_pos[1] - wall.start_pos[1])
            pygame.draw.rect(self.surface, Color.GREEN, rect, 1)

        for food in self.foods:
            pygame.draw.circle(self.surface, Color.YELLOW, food.position, food.radius, 1)

        for character in self.characters:
            character.update(delta_time=delta_time)

            # Use AABB check to clamp character position
            x, y = character.position
            if (x - character.radius) < self.min_x:
                x = self.min_x + character.radius
            elif (x + character.radius) > self.max_x:
                x = self.max_x - character.radius

            if (y - character.radius) < self.min_y:
                y = self.min_y + character.radius
            elif (y + character.radius) > self.max_y:
                y = self.max_y - character.radius

            character.position = (x, y)

            character.draw(self)
