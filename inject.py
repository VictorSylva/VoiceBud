"""Text injection at the cursor: clipboard + synthesized paste (Cmd+V on macOS, Ctrl+V on Windows),
with a per-character Unicode keystroke fallback. Saves/restores the clipboard."""
import sys
import time

try:
    import pyperclip
except ImportError:
    pyperclip = None

from pynput.keyboard import Controller, Key

_keyboard = Controller()
IS_MACOS = sys.platform == "darwin"

if IS_MACOS:
    try:
        import Quartz
        from AppKit import NSPasteboard, NSPasteboardTypeString
        KEY_V = 9  # macOS virtual keycode for 'v'
    except ImportError:
        Quartz = None
else:
    Quartz = None


def _set_clipboard(text):
    if pyperclip is not None:
        try:
            pyperclip.copy(text)
            return
        except Exception:
            pass
    if IS_MACOS and Quartz is not None:
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setString_forType_(text, NSPasteboardTypeString)


def _get_clipboard():
    if pyperclip is not None:
        try:
            return pyperclip.paste()
        except Exception:
            pass
    if IS_MACOS and Quartz is not None:
        pb = NSPasteboard.generalPasteboard()
        return pb.stringForType_(NSPasteboardTypeString)
    return None


def _press_paste():
    """Synthesize paste shortcut (Cmd+V on macOS, Ctrl+V on Windows/Linux)."""
    if IS_MACOS and Quartz is not None:
        src = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
        down = Quartz.CGEventCreateKeyboardEvent(src, KEY_V, True)
        up = Quartz.CGEventCreateKeyboardEvent(src, KEY_V, False)
        Quartz.CGEventSetFlags(down, Quartz.kCGEventFlagMaskCommand)
        Quartz.CGEventSetFlags(up, Quartz.kCGEventFlagMaskCommand)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, down)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, up)
    else:
        # Windows / Linux: Ctrl+V via pynput
        with _keyboard.pressed(Key.ctrl):
            _keyboard.press("v")
            _keyboard.release("v")


# Retain alias for any legacy callers
_press_cmd_v = _press_paste


def _type_unicode(text):
    """Fallback: per-character Unicode keystrokes (no clipboard involved)."""
    if IS_MACOS and Quartz is not None:
        src = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
        for ch in text:
            down = Quartz.CGEventCreateKeyboardEvent(src, 0, True)
            Quartz.CGEventKeyboardSetUnicodeString(down, len(ch), ch)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, down)
            up = Quartz.CGEventCreateKeyboardEvent(src, 0, False)
            Quartz.CGEventKeyboardSetUnicodeString(up, len(ch), ch)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, up)
            time.sleep(0.002)
    else:
        # pynput handles unicode typing natively across Windows and Linux
        _keyboard.type(text)


def inject(text, cfg):
    if not text:
        return
    if cfg.get("method", "paste") == "type":
        _type_unicode(text)
        return
    old = _get_clipboard() if cfg.get("restore_clipboard", True) else None
    _set_clipboard(text)
    time.sleep(0.05)  # let the pasteboard settle
    _press_paste()
    if old is not None:
        time.sleep(0.25)  # let the paste land before restoring
        _set_clipboard(old)
