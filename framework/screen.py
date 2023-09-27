import typing
from enum import IntEnum
from collections import defaultdict

import pygame


S = typing.TypeVar('S', bound='ScreenBase')


class Event(IntEnum):
    QUIT = pygame.USEREVENT + 1
    GAME_OVER = pygame.USEREVENT + 2
    START_GAME = pygame.USEREVENT + 3


class ScreenBase:
    def __init__(self, display: pygame.Surface, clock: pygame.Clock, state: typing.Optional[typing.Any]):
        self.display = display
        self.clock = clock
        self.state = state
        self._event_mapping: dict[int, list] = defaultdict(list)
        self._mouse_pos_callbacks = []
        self._subscreens: list[ScreenBase] = []
        self.add_event_listener(event_type=pygame.QUIT,
                                callback=lambda x: pygame.event.post(pygame.event.Event(Event.QUIT)))

    def tick(self, events: list[pygame.Event]):
        self._process_events(events=events)
        self.update()
        for s in self._subscreens:
            s.update()
        self.draw()
        for s in self._subscreens:
            s.draw()

    def add_event_listener(self, event_type: int, callback: callable):
        self._event_mapping[event_type].append(callback)

    def add_mouse_pos_callback(self, callback: callable):
        self._mouse_pos_callbacks.append(callback)

    def add_subscreen(self, s: S):
        self._subscreens.append(s)

    def _process_events(self, events: list[pygame.Event]):
        mouse_pos = pygame.mouse.get_pos()
        for c in self._mouse_pos_callbacks:
            c(mouse_pos)

        for s in self._subscreens:
            for c in s._mouse_pos_callbacks:
                c(mouse_pos)

        for event in events:
            if event.type in self._event_mapping:
                for c in self._event_mapping[event.type]:
                    c(event)
            for s in self._subscreens:
                if event.type in s._event_mapping:
                    for c in s._event_mapping[event.type]:
                        c(event)

    def update(self):
        pass

    def draw(self):
        pass

