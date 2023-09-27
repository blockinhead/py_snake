import pygame

from framework.screen import ScreenBase


class Label(ScreenBase):
    def __init__(self, display: pygame.Surface, clock: pygame.Clock,
                 center_pos: tuple[float, float], text: str, font: pygame.Font, color):
        super().__init__(display, clock, state=None)

        x_pos, y_pos = center_pos
        self.color = color
        self.text = text
        self.font = font

        _text = self.font.render(self.text, antialias=True, color=self.color)
        self.rect = _text.get_rect(center=(x_pos, y_pos))

    def draw(self):
        text = self.font.render(self.text, antialias=True, color=self.color)
        self.display.blit(text, self.rect)


class Button(Label):
    def __init__(self, display: pygame.Surface, clock: pygame.Clock,
                 center_pos: tuple[float, float], text: str, font: pygame.Font, base_color, over_color,
                 on_pressed: callable):
        super().__init__(display, clock, center_pos, text, font, base_color)

        self.base_color = base_color
        self.over_color = over_color
        self.on_pressed = on_pressed

        self.mouse_pos: tuple[int, int] = tuple()
        self.add_mouse_pos_callback(self.get_mouse_pos)
        self.add_event_listener(pygame.MOUSEBUTTONDOWN, self.check_button_pressed)

    def update(self):
        self.color = self.over_color if self.mouse_over_button() else self.base_color

    def get_mouse_pos(self, pos: tuple[int, int]):
        self.mouse_pos = pos

    def check_button_pressed(self, event: pygame.Event):
        if self.mouse_over_button():
            self.on_pressed()

    def mouse_over_button(self) -> bool:
        return self.rect.left <= self.mouse_pos[0] <= self.rect.right and \
            self.rect.top <= self.mouse_pos[1] <= self.rect.bottom

