from mathdash.sound import GameSound
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class GameInfo:
    name: str
    description: str
    gimmick: str
    difficult: int

    @classmethod
    def from_json(cls, data: dict) -> "GameInfo":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            gimmick=data.get("gimmick", ""),
            difficult=data.get("difficult", 0),
        )


@dataclass
class LoadInfo:
    description: str = ""
    progress: int = 0
    max_progress: int = 0
    complete: bool = False


class Stage(ABC):
    def __init__(self):
        self.data: dict | None = None
        self.music: GameSound | None = None
        self._info: GameInfo | None = None

    @property
    def info(self) -> GameInfo:
        return self._info

    @abstractmethod
    def load(self):
        pass
