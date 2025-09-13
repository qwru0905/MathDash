import os
os.environ["PYFMODEX_DLL_PATH"] = "assets/fmod.dll"
import pyfmodex as fmod
from pyfmodex.enums import TIMEUNIT
from pyfmodex.flags import MODE

g_initialized: bool = False

SOUND_MAX = 1.0
SOUND_MIN = 0.0
SOUND_DEFAULT = 0.5
SOUND_WEIGHT = 0.1

MIN_FMOD_VERSION = 0x00020108


class GameSound:
    def __init__(self, path: str, loop: bool = False):
        if not g_initialized:
            self.system = fmod.System()
            self.system.init()

        mode = MODE.LOOP_NORMAL if loop else MODE.DEFAULT

        self.sound = self.system.create_sound(path, mode=mode)
        self.channel = None
        self.volume = SOUND_DEFAULT

    def play(self):
        self.channel = self.system.play_sound(self.sound)

        if self.channel:
            self.channel.volume = self.volume

    def pause(self):
        self.channel.paused = True

    def resume(self):
        self.channel.paused = False

    def stop(self):
        self.channel.stop()

    def volume_up(self):
        if self.volume < SOUND_MAX:
            self.volume += SOUND_WEIGHT
            if self.volume > SOUND_MAX:
                self.volume = SOUND_MAX

        if self.channel:
            self.channel.volume = self.volume

    def volume_down(self):
        if self.volume > SOUND_MIN:
            self.volume -= SOUND_WEIGHT
            if self.volume > SOUND_MIN:
                self.volume = SOUND_MIN

        if self.channel:
            self.channel.volume = self.volume

    def get_position(self):
        if not self.channel:
            return -1

        position = self.channel.get_position(TIMEUNIT.MS)
        return position

    def set_position(self, position: int):
        if not self.channel:
            return

        self.channel.set_position(position, TIMEUNIT.MS)
