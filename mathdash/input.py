from dataclasses import dataclass


@dataclass
class ButtonState:
    is_down: bool = False
    changed: bool = False


class Input:
    def __init__(self):
        self.buttons = [ButtonState() for _ in range(10)]
