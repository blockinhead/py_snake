import random
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Self, Optional, Sequence

import pygame

from framework.elements import Label
from framework.screen import Event, ScreenBase


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class FoodType(Enum):
    GENERAL = 1
    SLOWER = 2
    SUPER = 3


@dataclass(eq=True, frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return Position(self.x + other.x, self.y + other.y)


@dataclass(frozen=True)
class Food:
    # position: Position
    type: FoodType
    time_to_live: float  # ms


class State:
    direction_to_pos_delta = {Direction.RIGHT: Position(1, 0),
                              Direction.LEFT: Position(-1, 0),
                              Direction.UP: Position(0, -1),
                              Direction.DOWN: Position(0, 1)}

    def __init__(self):
        self.snake: deque[Position] = deque((Position(1, 8), Position(1, 9), Position(1, 10)))
        self.food: dict[Position: Food] = {}
        self.direction: Direction = Direction.RIGHT
        self._last_tick = None

        self.num_cells = 20
        self.max_ticks_to_update = 400  # ms
        self.min_ticks_to_update = 100
        self.ticks_delta = 50
        self.ticks_to_update = self.max_ticks_to_update
        self.last_update = 0
        self.max_food = 3

        self.score = 0

        self._add_food()

    def update(self, new_direction: Optional[Direction] = None, tick: int = 0) -> Optional[Event]:
        if new_direction:
            self.direction = new_direction

        if self._last_tick is None:
            self._last_tick = tick
            return

        delta_tick = tick - self._last_tick
        self._last_tick = tick
        self.last_update += delta_tick

        self._update_food(delta_tick)

        if self.last_update < self.ticks_to_update:
            return

        self.last_update -= self.ticks_to_update

        new_head_pos = self.snake[0] + self.direction_to_pos_delta[self.direction]
        if not (0 <= new_head_pos.x < self.num_cells) or not (0 <= new_head_pos.y < self.num_cells) \
                or new_head_pos in self.snake:
            return Event.GAME_OVER

        self.snake.appendleft(new_head_pos)
        if self.snake[0] in self.food:
            self._eat_food(self.snake[0])
        else:
            self.snake.pop()

    def _eat_food(self, food_pos: Position):
        if self.food[food_pos].type == FoodType.GENERAL:
            self.score += 1
            self.ticks_to_update = max(self.min_ticks_to_update, self.ticks_to_update - self.ticks_delta)

        elif self.food[food_pos].type == FoodType.SUPER:
            self.score += 3

        elif self.food[food_pos].type == FoodType.SLOWER:
            self.ticks_to_update = min(self.max_ticks_to_update, self.ticks_to_update + self.ticks_delta)

        self.food.pop(food_pos)
        self._add_food()

    def _add_food(self):
        p = Position(random.randrange(self.num_cells), random.randrange(self.num_cells))
        if p in self.snake or p in self.food:
            self._add_food()

        _food = Food(type=random.choices(list(FoodType), weights=[4, 2, 1])[0],
                     time_to_live=random.randint(6000, 10000))
        self.food[p] = _food

    def _update_food(self, delta_tick: int):

        if len(self.food) < self.max_food:
            if random.random() > 0.95:
                self._add_food()

        for p in list(self.food.keys()):

            t = self.food[p].time_to_live - delta_tick
            if t < 0:
                self.food.pop(p)
            else:
                self.food[p] = Food(type=self.food[p].type,
                                    time_to_live=t)


class Game(ScreenBase):
    width = 800
    height = 600
    cell_size = 25
    filed_offset = 20
    snake_color = 'chartreuse3'
    border_color = 'burlywood4'

    food_color = {
        FoodType.GENERAL: 'brown1',
        FoodType.SUPER: 'chocolate1',
        FoodType.SLOWER: 'darkgoldenrod1',
    }

    def __init__(self, display: pygame.Surface, clock: pygame.Clock, state: State):
        super().__init__(display, clock, state)
        self.add_event_listener(event_type=pygame.KEYDOWN, callback=self.get_input)
        self.direction: Optional[Direction] = None

        self.score_label = Label(display=display,
                                 clock=clock,
                                 center_pos=(self.width - 100, self.height - 500),
                                 text='Score: %02d' % self.state.score,
                                 color='black',
                                 font=pygame.Font(None, 40))

        self.add_subscreen(self.score_label)

    def update(self):
        if event := self.state.update(self.direction, pygame.time.get_ticks()):
            pygame.event.post(pygame.event.Event(event))

        self.score_label.text = 'Score: %02d' % self.state.score

    def draw(self):
        self.display.fill('gray')

        self._draw_borders()

        for pos in self.state.food:
            self._draw_rect(surface=self.display,
                            pos=pos + Position(1, 1),
                            color=self.food_color[self.state.food[pos].type])

        for snake_elem in self.state.snake:
            self._draw_rect(surface=self.display, pos=snake_elem + Position(1, 1), color=self.snake_color)

    def _draw_rect(self, surface: pygame.Surface, pos: Position, color: int | str | Sequence[int]):
        pygame.draw.rect(
            surface=surface,
            color=color,
            rect=pygame.Rect(pos.x * self.cell_size + self.filed_offset, pos.y * self.cell_size + self.filed_offset,
                             self.cell_size, self.cell_size),
            width=0
        )

    def _draw_borders(self):
        p = Position(0, 0)
        for i in range(self.state.num_cells + 1):
            self._draw_rect(surface=self.display, pos=p, color=self.border_color)
            p = p + Position(0, 1)

        p = Position(0, 0)
        for i in range(self.state.num_cells + 1):
            self._draw_rect(surface=self.display, pos=p, color=self.border_color)
            p = p + Position(1, 0)

        p = Position(self.state.num_cells + 1, 0)
        for i in range(self.state.num_cells + 1):
            self._draw_rect(surface=self.display, pos=p, color=self.border_color)
            p = p + Position(0, 1)

        p = Position(0, self.state.num_cells + 1)
        for i in range(self.state.num_cells + 2):
            self._draw_rect(surface=self.display, pos=p, color=self.border_color)
            p = p + Position(1, 0)

    def get_input(self, event: pygame.Event):
        direction = None
        if event.key == pygame.K_UP:
            direction = Direction.UP
        if event.key == pygame.K_DOWN:
            direction = Direction.DOWN
        if event.key == pygame.K_LEFT:
            direction = Direction.LEFT
        if event.key == pygame.K_RIGHT:
            direction = Direction.RIGHT

        self.direction = direction
