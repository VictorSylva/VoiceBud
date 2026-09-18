"""System-wide push-to-talk hotkey via pynput.

Supports single keys ("alt_r", "ctrl_r") or chords ("ctrl+shift", "ctrl+alt"), and two modes:
  hold   — record while keys are held, stop on release
  toggle — press the chord once to start, press again to stop
"""
from pynput import keyboard

# Define available keys in KEY_MAP
KEY_MAP = {
    "alt": keyboard.Key.alt,
    "alt_l": getattr(keyboard.Key, "alt_l", keyboard.Key.alt),
    "alt_r": keyboard.Key.alt_r,
    "ctrl": keyboard.Key.ctrl,
    "ctrl_l": getattr(keyboard.Key, "ctrl_l", keyboard.Key.ctrl),
    "ctrl_r": keyboard.Key.ctrl_r,
    "cmd": keyboard.Key.cmd,
    "cmd_l": getattr(keyboard.Key, "cmd_l", keyboard.Key.cmd),
    "cmd_r": keyboard.Key.cmd_r,
    "win": keyboard.Key.cmd,
    "win_l": getattr(keyboard.Key, "cmd_l", keyboard.Key.cmd),
    "win_r": keyboard.Key.cmd_r,
    "windows": keyboard.Key.cmd,
    "shift": keyboard.Key.shift,
    "shift_l": getattr(keyboard.Key, "shift_l", keyboard.Key.shift),
    "shift_r": keyboard.Key.shift_r,
    "f1": keyboard.Key.f1,
    "f2": keyboard.Key.f2,
    "f3": keyboard.Key.f3,
    "f4": keyboard.Key.f4,
    "f5": keyboard.Key.f5,
    "f6": keyboard.Key.f6,
    "f7": keyboard.Key.f7,
    "f8": keyboard.Key.f8,
    "f9": keyboard.Key.f9,
    "f10": keyboard.Key.f10,
    "f11": keyboard.Key.f11,
    "f12": keyboard.Key.f12,
    "f13": keyboard.Key.f13,
}

# Group variants so generic "ctrl" matches left or right Ctrl on Windows & Mac
def _get_allowed_keys_for_name(name):
    target = KEY_MAP[name]
    if name == "ctrl":
        variants = {keyboard.Key.ctrl, getattr(keyboard.Key, "ctrl_l", None), getattr(keyboard.Key, "ctrl_r", None)}
    elif name == "shift":
        variants = {keyboard.Key.shift, getattr(keyboard.Key, "shift_l", None), getattr(keyboard.Key, "shift_r", None)}
    elif name == "alt":
        variants = {keyboard.Key.alt, getattr(keyboard.Key, "alt_l", None), getattr(keyboard.Key, "alt_r", None), getattr(keyboard.Key, "alt_gr", None)}
    elif name in ("cmd", "win", "windows"):
        variants = {keyboard.Key.cmd, getattr(keyboard.Key, "cmd_l", None), getattr(keyboard.Key, "cmd_r", None)}
    else:
        variants = {target}
    return {k for k in variants if k is not None}


class PushToTalk:
    def __init__(self, key_name, on_press, on_release, mode="hold"):
        names = [n.strip().lower() for n in key_name.split("+")]
        unknown = [n for n in names if n not in KEY_MAP]
        if unknown:
            raise ValueError(f"Unknown hotkey(s) {unknown}. Choose from: {list(KEY_MAP)}")

        # List of sets of keys, each representing a required slot in the chord
        self._slots = [_get_allowed_keys_for_name(n) for n in names]
        self._all_watched_keys = set().union(*self._slots)
        self.mode = mode
        self.on_press_cb = on_press
        self.on_release_cb = on_release

        self._down = set()
        self._chord_held = False   # chord physically complete right now
        self._recording = False    # logical recording state (drives toggle mode)
        self._listener = keyboard.Listener(on_press=self._press, on_release=self._release)

    def _is_chord_satisfied(self):
        return all(any(k in self._down for k in slot) for slot in self._slots)

    def _press(self, key):
        if key not in self._all_watched_keys:
            return
        self._down.add(key)
        satisfied = self._is_chord_satisfied()

        if not self._chord_held and satisfied:
            self._chord_held = True
            if self.mode == "toggle":
                if self._recording:
                    self._recording = False
                    self.on_release_cb()
                else:
                    self._recording = True
                    self.on_press_cb()
            else:  # hold
                self._recording = True
                self.on_press_cb()

    def _release(self, key):
        if key not in self._all_watched_keys:
            return
        self._down.discard(key)
        satisfied = self._is_chord_satisfied()

        if self._chord_held and not satisfied:
            self._chord_held = False
            if self.mode == "hold" and self._recording:
                self._recording = False
                self.on_release_cb()

    def start(self):
        """Start listening without blocking."""
        self._listener.start()

    def run(self):
        self._listener.start()
        self._listener.join()
