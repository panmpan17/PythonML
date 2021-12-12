import pygame
import math
from typing import List
from scripts.pygame_foundation import Color, Entity, InputSystem, KeyCode, ManagedWindow, Math, Vector


class Character(Entity):
    def __init__(self, position:Vector, move_speed) -> None:
        super().__init__()

        self.rotation_speed = 0.1
        self.move_speed = move_speed
        self.position: Vector = position

        self._rotation = 0
        self.direction: Vector = (math.cos(0), math.sin(0))

        self.radius = 10

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.direction = (math.cos(value), math.sin(value))

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
    
    def draw(self, window: ManagedWindow):
        pygame.draw.circle(window.surface, Color.GREEN, self.position, self.radius, 2)
        pygame.draw.line(window.surface, Color.RED, self.position,
                         Math.tuple_plus(self.position, Math.tuple_multiple(self.direction, 20)))


class NavigationGame(ManagedWindow):
    def __init__(self, tick_limit=False) -> None:
        super().__init__((400, 400), step_update=False, tick=30, tick_limit=tick_limit)

        self.characters: List[Character] = []

    def update(self, delta_time: float):
        for character in self.characters:
            x, y = character.position
            if (x - character.radius) < 0:
                x = character.radius
            elif (x + character.radius) > 400:
                x = 400 - character.radius

            if (y - character.radius) < 0:
                y = character.radius
            elif (y + character.radius) > 400:
                y = 400 - character.radius

            character.position = (x, y)
