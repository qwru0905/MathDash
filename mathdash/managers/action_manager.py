from dataclasses import dataclass
from .utils import make_ease
from easing_functions.easing import EasingBase
from .decoration_manager import Decoration


@dataclass
class ProgressAction:
    dec: Decoration
    key: str
    ease: EasingBase
    start_time: float
    index: int | None = None


def get_default(key):
    if key in ["pos_offset", "scale"]:
        return [0, 0]

    if key in ["rotation"]:
        return 0

    if key in ["opacity"]:
        return 100


class ActionManager:
    def __init__(self):
        self.actions: list[dict] = []
        self.progress_actions: list[ProgressAction] = []

    def add_action(self, action: dict):
        self.actions.append(action)

    def update(self, now: float, find_decorations):
        # 실행할 액션 찾아 적용
        pending_remove = []
        for act in self.actions:
            if act["time"] <= now:
                for dec in find_decorations(act["tag"]):
                    for key, value in act.items():
                        # pos_offset 처리 (x, y 따로)
                        if key in ["pos_offset", "scale"]:
                            start_val = getattr(dec, key, get_default(key))
                            target_val = act.get(key, [None, None])
                            for i in (0, 1):  # x=0, y=1
                                if target_val[i] is None:
                                    continue

                                ease = make_ease(
                                    act.get("ease", "linear"),
                                    start_val[i],
                                    target_val[i],
                                    act["duration"]
                                )
                                self.progress_actions.append(
                                    ProgressAction(dec, key, ease, act["time"], i)
                                )

                        # opacity 처리
                        if key in ["rotation", "opacity"]:
                            start_val = getattr(dec, key, get_default(key))
                            target_val = act.get(key, None)

                            if target_val is None:
                                continue

                            ease = make_ease(
                                act.get("ease", "linear"),
                                start_val,
                                target_val,
                                act["duration"]
                            )
                            self.progress_actions.append(
                                ProgressAction(dec, key, ease, act["time"])
                            )

                pending_remove.append(act)

        for act in pending_remove:
            self.actions.remove(act)

        # 진행 중 액션 업데이트
        alive = []
        for pa in self.progress_actions:
            t = now - pa.start_time
            if t <= pa.ease.duration:
                value = pa.ease(t)

                if pa.key in ["rotation", "opacity"]:
                    setattr(pa.dec, pa.key, value)
                elif pa.key in ["pos_offset", "scale"] and pa.index is not None:
                    getattr(pa.dec, pa.key)[pa.index] = value

                alive.append(pa)
            else:
                value = pa.ease.end

                if pa.key in ["rotation", "opacity"]:
                    setattr(pa.dec, pa.key, value)
                elif pa.key in ["pos_offset", "scale"] and pa.index:
                    getattr(pa.dec, pa.key)[pa.index] = value
        self.progress_actions = alive
