import asyncio

import pygame

from framework.screen import Event
from screens.game import Game, State
from screens.game_over import GameOver


class Main:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode([Game.width, Game.height])
        self.clock = pygame.time.Clock()
        self.game: Game = None
        self.state: State = None
        self._init_new_game()
        self.game_over = GameOver(display=self.display, clock=self.clock, state=self.state)
        self.screen = self.game

    def _init_new_game(self):
        self.state = State()
        self.game = Game(display=self.display, clock=self.clock, state=self.state)

    async def main(self):
        run = True
        while run:
            events = pygame.event.get()
            for event in events:
                if event.type == Event.QUIT:
                    run = False
                elif event.type == Event.GAME_OVER:
                    self.screen = self.game_over
                elif event.type == Event.START_GAME:
                    self._init_new_game()
                    self.screen = self.game

            self.screen.tick(events=events)
            pygame.display.update()
            self.clock.tick(60)
            await asyncio.sleep(0)
        pygame.quit()


if __name__ == '__main__':
    main = Main()
    asyncio.run(main.main())
