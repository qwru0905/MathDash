from abc import ABC, abstractmethod


class Tab(ABC):
    @abstractmethod
    def open_file(self, file_path):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def event(self, events):
        pass

    @abstractmethod
    def draw(self, surface):
        pass
