from typing import Any

import pygame

from framework.screen import ScreenBase, Event
from framework.elements import Button, Label


class GameOver(ScreenBase):
    text_color = 'black'

    def __init__(self, display: pygame.Surface, clock: pygame.Clock, state: Any):
        super().__init__(display, clock, state)

        self.font = pygame.font.Font(None, 40)

        self.add_subscreen(Button(display, clock,
                                  center_pos=(self.display.get_width() / 2,
                                              self.display.get_height() / 2 + 40),
                                  text='Start New Game',
                                  font=pygame.Font(None, 45),
                                  base_color='black',
                                  over_color='red',
                                  on_pressed=lambda: pygame.event.post(pygame.event.Event(Event.START_GAME))
                                  ))

        self.add_subscreen(Label(display, clock,
                                 center_pos=(self.display.get_width() / 2,
                                             self.display.get_height() / 2 - 20),
                                 text='Game Over',
                                 font=pygame.Font(None, 40),
                                 color='black'))

    def draw(self):
        rect = pygame.Rect(75, 75, 675, 475)
        background = pygame.Surface(size=rect.size, flags=pygame.SRCALPHA)
        pygame.draw.rect(background, [100, 100, 100, 10], background.get_rect())
        self.display.blit(background, rect)
