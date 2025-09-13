import os
from typing import Optional

os.environ["PYFMODEX_DLL_PATH"] = "assets/fmod.dll"

import pyfmodex as fmod
from pyfmodex.enums import TIMEUNIT
from pyfmodex.flags import MODE


class GameSound:
    """게임 사운드 관리 클래스"""

    SOUND_MAX = 1.0
    SOUND_MIN = 0.0
    SOUND_DEFAULT = 0.5
    SOUND_STEP = 0.1

    MIN_FMOD_VERSION = 0x00020108

    # 모든 GameSound 인스턴스가 공유할 FMOD 시스템
    _system: Optional[fmod.System] = None

    def __init__(self, path: str, loop: bool = False):
        if GameSound._system is None:
            GameSound._system = fmod.System()
            GameSound._system.init()

        mode = MODE.LOOP_NORMAL if loop else MODE.DEFAULT

        self.sound = GameSound._system.create_sound(path, mode=mode)
        self.channel: Optional[fmod.channel.Channel] = None
        self.volume: float = self.SOUND_DEFAULT

    # ----------------------
    # 재생 관련
    # ----------------------
    def play(self) -> None:
        """사운드 재생"""
        self.channel = GameSound._system.play_sound(self.sound)
        self._apply_volume()

    def pause(self) -> None:
        if self.channel:
            self.channel.paused = True

    def resume(self) -> None:
        if self.channel:
            self.channel.paused = False

    def stop(self) -> None:
        if self.channel:
            self.channel.stop()

    # ----------------------
    # 볼륨 관련
    # ----------------------
    def _apply_volume(self) -> None:
        """현재 볼륨을 채널에 반영"""
        if self.channel:
            self.channel.volume = self.volume

    def set_volume(self, value: float) -> None:
        """볼륨을 직접 설정"""
        self.volume = max(self.SOUND_MIN, min(self.SOUND_MAX, value))
        self._apply_volume()

    def volume_up(self) -> None:
        """볼륨 증가"""
        self.set_volume(self.volume + self.SOUND_STEP)

    def volume_down(self) -> None:
        """볼륨 감소"""
        self.set_volume(self.volume - self.SOUND_STEP)

    # ----------------------
    # 위치 관련
    # ----------------------
    def get_position(self) -> int:
        """현재 재생 위치(ms). 채널이 없으면 -1 반환"""
        if not self.channel:
            return -1
        return self.channel.get_position(TIMEUNIT.MS)

    def set_position(self, position: int) -> None:
        """재생 위치를 ms 단위로 이동"""
        if self.channel:
            self.channel.set_position(position, TIMEUNIT.MS)
