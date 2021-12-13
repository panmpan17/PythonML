import random
import pygame
import math
import json
import os

from scripts.NEAT.functions import connection_mutations, insert_node_mutations
from .utilities import ProgressBar
from enum import Enum
from .NEAT import Genome, genome_feed_data, connection_weight_random_add
from .pygame_foundation import Color, Entity, InputSystem, KeyCode, Math, Vector
from .NEAT_pygame import NEATManagedWindow
from dataclasses import dataclass
from typing import List, Tuple


class HitType(Enum):
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
    def __init__(self, position:Vector, move_speed, rotation_speed=0.1) -> None:
        super().__init__()

        self.rotation_speed = rotation_speed
        self.move_speed = move_speed
        self.position: Vector = position

        self._rotation = 0
        self.direction: Vector = (math.cos(0), math.sin(0))
        self.raycasts: List[RaycastData] = []

        self.radius = 10

        self.game: NavigationGame = None
        self.food_count = 0

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

        # Shoot out raycast from relative angle -45 to 45 every 5 degree
        for rotation_delta in range(-45, 45 + 1, 15):
            angle = self._rotation + (rotation_delta / 60)
            direction = (math.cos(angle), math.sin(angle))

            # Add raycast info and result
            type_, hit_point  = self.game.raycast(self.position, direction)

            self.raycasts.append(RaycastData(
                direction,
                hit_point,
                type_,
                Math.magnitude(self.position, hit_point)))

    def update(self, delta_time: float):
        # Handle turning
        direction_changes = 0
        if InputSystem.check_key_pressed(KeyCode.A):
            direction_changes -= 1
        if InputSystem.check_key_pressed(KeyCode.D):
            direction_changes += 1

        if direction_changes != 0:
            self.rotation += direction_changes * self.rotation_speed * delta_time

        # Handle moving forward
        if InputSystem.check_key_pressed(KeyCode.W):
            self.position = (self.position[0] + (self.direction[0] * self.move_speed * delta_time),
                            self.position[1] + (self.direction[1] * self.move_speed * delta_time))
            self.recalculate_raycasts()
    
    def draw(self, window: NEATManagedWindow):
        pygame.draw.circle(window.surface, Color.GREEN, self.position, self.radius, 2)
        # Draw facing
        # pygame.draw.line(window.surface, Color.YELLOW, self.position,
        #                  Math.tuple_plus(self.position, Math.tuple_multiple(self.direction, 40)))

        # Draw raycast direciton
        for raycast in self.raycasts:
            if raycast.hit_type == HitType.Nothing:
                pygame.draw.line(window.surface, Color.GRAY, self.position, raycast.hit_point)
            elif raycast.hit_type == HitType.Wall:
                pygame.draw.line(window.surface, Color.GREEN, self.position, raycast.hit_point)
            elif raycast.hit_type == HitType.Food:
                pygame.draw.line(window.surface, Color.YELLOW, self.position, raycast.hit_point)


class GenomeCharacter(Character):
    def __init__(self, genome:Genome, position: Vector, move_speed) -> None:
        super().__init__(position, move_speed)

        self.genome = genome
        self.score = 0

    def update(self, delta_time: float):
        inputs = [self.position[0], self.position[1]]
        for racast in self.raycasts:
            inputs.append(racast.hit_type.value)
            inputs.append(racast.distance)

        results = genome_feed_data(
            genome=self.genome,
            inputs=inputs)

        direction_changes = 0
        if results[0] > 0:
            direction_changes -= 1
        if results[1] > 1:
            direction_changes += 1
        
        if direction_changes != 0:
            self.rotation += direction_changes * self.rotation_speed * delta_time

        if results[2]:
            self.position = (self.position[0] + (self.direction[0] * self.move_speed * delta_time),
                            self.position[1] + (self.direction[1] * self.move_speed * delta_time))
            self.recalculate_raycasts()


class NavigationGame(NEATManagedWindow):
    def __init__(self, run_pygame, tick_limit=False) -> None:
        super().__init__(
            run_pygame=run_pygame,
            size=(400, 200),
            tick_limit=tick_limit)
        self.min_x = 10
        self.max_x = 390
        self.min_y = 10
        self.max_y = 190

        self.characters: List[GenomeCharacter] = []
        self.walls: List[Wall] = []

        # self.walls.append(Wall((40, 60), (100, 90)))
        # self.walls.append(Wall((100, 300), (150, 400)))

        self.foods: List[Food] = []
        self.foods.append(Food((350, 100), 5))
        self.foods.append(Food((50, 100), 5))
        self.foods.append(Food((350, 150), 5))
        self.foods.append(Food((50, 150), 5))
        self.foods.append(Food((350, 50), 5))
        self.foods.append(Food((50, 50), 5))

        self.time_pass = 0
        self.time_pass_limit = 100

        self.progress_bar = ProgressBar(self.time_pass_limit, length=40)

    def add_character(self, character: Character):
        self.characters.append(character)
        character.game = self
        character.recalculate_raycasts()

    def raycast(self, position:Vector, direction:Vector, max_distance=30) -> Tuple[HitType, Vector]:
        direction = Math.tuple_multiple(direction, 3)
        for _ in range(max_distance):
            position = Math.tuple_plus(position, direction)

            # Check borders for raycast
            if position[0] <= self.min_x:
                return HitType.Wall, position
            if position[1] <= self.min_y:
                return HitType.Wall, position
            if position[0] >= self.max_x:
                return HitType.Wall, position
            if position[1] >= self.max_y:
                return HitType.Wall, position

            # Check walls for raycast
            for wall in self.walls:
                if wall.end_pos[0] > position[0] > wall.start_pos[0]:
                    if wall.end_pos[1] > position[1] > wall.start_pos[1]:
                        return HitType.Wall, position

            # Check foods for raycast
            for food in self.foods:
                if Math.sqr_magnitude(position, food.position) <= food.radius * food.radius:
                    return HitType.Food, position

        return HitType.Nothing, position

    def update(self, delta_time: float):
        if self.run_pygame:
            pygame.draw.line(self.surface, Color.GREEN, (self.min_x, self.min_y), (self.min_x, self.max_y))
            pygame.draw.line(self.surface, Color.GREEN, (self.min_x, self.max_y), (self.max_x, self.max_y))
            pygame.draw.line(self.surface, Color.GREEN, (self.max_x, self.max_y), (self.max_x, self.min_y))
            pygame.draw.line(self.surface, Color.GREEN, (self.max_x, self.min_y), (self.min_x, self.min_y))

        for wall in self.walls:
            rect = (*wall.start_pos, wall.end_pos[0] - wall.start_pos[0], wall.end_pos[1] - wall.start_pos[1])
            if self.run_pygame:
                pygame.draw.rect(self.surface, Color.GREEN, rect, 1)

        for i, food in enumerate(self.foods):
            color = (((i + 1) / len(self.foods)) * 255, ((i + 1) / len(self.foods)) * 255, 0)
            if self.run_pygame:
                pygame.draw.circle(self.surface, color, food.position, food.radius, 1)

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

            #  Check touched food
            # for food in self.foods:
            food = self.foods[character.food_count]
            if Math.sqr_magnitude(character.position, food.position) <= ((food.radius + character.radius) ** 2):
                character.food_count += 1

            if character.food_count >= len(self.foods):
                self.reset()
                return

            if self.run_pygame:
                character.draw(self)

        self.time_pass += delta_time
        if self.time_pass > self.time_pass_limit:
            self.reset()
            return
        
        self.progress_bar.set_progress(self.time_pass)

    def evaluate_character_score(self):
        max_distance = 400 * 400 + 200 * 200
        for character in self.characters:
            score = character.food_count

            if character.food_count >= len(self.foods):
                distance = 0
            else:
                distance = Math.sqr_magnitude(character.position, self.foods[character.food_count].position)

            score += 1 - (distance / max_distance)
            character.score = score

    def reset(self):
        self.total_round += 1
        self.generation_round_count += 1

        self.progress_bar.set_progress(self.progress_bar.progress_length)
        self.time_pass = 0

        self.evaluate_character_score()
        best_characters = sorted(self.characters, key=lambda character: character.score, reverse=True)

        # Update high score
        self.update_high_score(best_characters[0].score)

        # Handle mutation
        if self.round_since_last_high_score >= 4:
            self.generation_count += 1
            self.generation_round_count = 0

            best_characters = best_characters[:20]
            self.round_since_last_high_score = 0

            self.save_characters(best_characters, str(self.generation_count))

            for character in best_characters:
                mutations = connection_mutations(character.genome, -4, 4)
                mutations += insert_node_mutations(character.genome)
                mutations = random.choices(mutations, k=10)

                for genome in mutations:
                    variants = connection_weight_random_add(genome, 20, -4, 4)
                    for variant in variants:
                        character = GenomeCharacter(variant, (50, 100), 10)
                        self.add_character(character=character)

        else:
            best_characters = best_characters[:20]
            self.characters.clear()

            for character in best_characters:
                variants = connection_weight_random_add(character.genome, 20, -4, 4)
                for variant in variants:
                    character = GenomeCharacter(variant, (50, 100), 10)
                    self.add_character(character=character)

    def run_without_pygame(self):
        # self.progress_bar.set_progress(0)
        delta_time = 1 / self.tick

        while True:
            self.update(delta_time)

    def save_characters(self, characters: List[GenomeCharacter], suffix=""):
        character_datas = []
        for character in characters:
            character_datas.append(character.genome.toJSON())

        file_path = os.path.join(os.getcwd(), "result", f"character-{suffix}.json")

        with open(file_path, "w") as f:
            json.dump(character_datas, f, default=lambda obj: obj.toJSON(), indent=2)

    def save_characters_unexpected_quit(self, number, suffix=""):
        self.evaluate_character_score()
        best_characters = sorted(self.characters, key=lambda character: character.score, reverse=True)
        if len(best_characters) > number:
            best_characters = best_characters[:number]

        character_datas = []
        for character in best_characters:
            character_datas.append(character.genome.toJSON())

        file_path = os.path.join(os.getcwd(), "result", f"character-{suffix}.json")

        with open(file_path, "w") as f:
            json.dump(character_datas, f, default=lambda obj: obj.toJSON(), indent=2)
