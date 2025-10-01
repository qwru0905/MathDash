from abc import ABC, abstractmethod


class Tab(ABC):
    @abstractmethod
    def open_file(self, base_path, data):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def event(self, events):
        pass

    @abstractmethod
    def draw(self):
        pass
