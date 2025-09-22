from mathdash.managers.note import Note


class NoteManager:
    def __init__(self, lane_count: int = 10):
        self.notes = [[] for _ in range(lane_count)]
        self.now_note = [0] * lane_count
        self.lane_count = lane_count

    def add_note(self, lane: int, equation: str, time: int, speed: int, x: int, y: int):
        self.notes[lane].append(Note(lane, equation, time, speed, x, y))

    def update(self, position: int):
        for line_idx, note_line in enumerate(self.notes):
            for note in note_line[self.now_note[line_idx]:]:
                if note.update(position) == -1:  # 끝난 노트 제거
                    self.now_note[line_idx] += 1

    def judge(self, lane: int, position: int) -> int:
        if lane < len(self.notes) and self.now_note[lane] < len(self.notes[lane]):
            result = self.notes[lane][self.now_note[lane]].judge(position)
            if result != 0:
                self.now_note[lane] += 1
            return result
        return 0

    def draw(self, screen):
        for line_idx, note_line in enumerate(self.notes):
            idx = self.now_note[line_idx]
            for note in note_line[idx:]:
                note.draw(screen)
