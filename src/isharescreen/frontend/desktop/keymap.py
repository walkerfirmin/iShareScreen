"""Translation tables: glfw input codes → wire-format codes.

GLFW reports physical keys (`GLFW_KEY_*`) and platform mouse buttons.
The host's RFB handler expects X11 keysyms for keys (`0xff08` =
Backspace, etc.) and Apple's non-standard pointer-button bitmask for
mouse (bit 1 = right, bit 2 = middle — see `protocol.rfb.BTN_*`).

Key events are split between two callbacks:
  * `set_key_callback`  — reports physical key + modifiers; we use it
                          for special keys (arrows, function, modifiers)
  * `set_char_callback` — reports the typed Unicode codepoint with the
                          user's current keyboard layout already
                          applied; we use it for printable characters
                          so AZERTY / Dvorak / Shift behave correctly.
"""
from __future__ import annotations

import glfw

from ...proxy.protocol.rfb import BTN_LEFT, BTN_MIDDLE, BTN_RIGHT


# Physical glfw key code → X11 keysym. Only special / non-printable
# keys belong here; printable ASCII is routed through char_callback so
# the user's keyboard layout is honoured — except when Ctrl/Super/Alt
# is held, because on_char does not fire then (see key_to_x11).
GLFW_KEY_TO_X11: dict[int, int] = {
    glfw.KEY_ESCAPE:        0xff1b,
    glfw.KEY_TAB:           0xff09,
    glfw.KEY_BACKSPACE:     0xff08,
    glfw.KEY_ENTER:         0xff0d,
    glfw.KEY_DELETE:        0xffff,
    glfw.KEY_INSERT:        0xff63,
    glfw.KEY_HOME:          0xff50,
    glfw.KEY_END:           0xff57,
    glfw.KEY_PAGE_UP:       0xff55,
    glfw.KEY_PAGE_DOWN:     0xff56,
    glfw.KEY_LEFT:          0xff51,
    glfw.KEY_UP:            0xff52,
    glfw.KEY_RIGHT:         0xff53,
    glfw.KEY_DOWN:          0xff54,
    glfw.KEY_LEFT_SHIFT:    0xffe1,
    glfw.KEY_RIGHT_SHIFT:   0xffe2,
    glfw.KEY_LEFT_CONTROL:  0xffe3,
    glfw.KEY_RIGHT_CONTROL: 0xffe4,
    glfw.KEY_LEFT_ALT:      0xffe9,
    glfw.KEY_RIGHT_ALT:     0xffea,
    glfw.KEY_LEFT_SUPER:    0xffeb,
    glfw.KEY_RIGHT_SUPER:   0xffec,
    glfw.KEY_CAPS_LOCK:     0xffe5,
    glfw.KEY_F1: 0xffbe, glfw.KEY_F2: 0xffbf, glfw.KEY_F3: 0xffc0,
    glfw.KEY_F4: 0xffc1, glfw.KEY_F5: 0xffc2, glfw.KEY_F6: 0xffc3,
    glfw.KEY_F7: 0xffc4, glfw.KEY_F8: 0xffc5, glfw.KEY_F9: 0xffc6,
    glfw.KEY_F10: 0xffc7, glfw.KEY_F11: 0xffc8, glfw.KEY_F12: 0xffc9,
}

# glfw KEY_* for US-layout punctuation/digits equal the ASCII codepoint.
# A–Z are 65–90; X11 letter keysyms are lowercase (97–122).
_GLFW_PRINTABLE_ASCII = frozenset({
    glfw.KEY_SPACE, glfw.KEY_APOSTROPHE, glfw.KEY_COMMA, glfw.KEY_MINUS,
    glfw.KEY_PERIOD, glfw.KEY_SLASH, glfw.KEY_SEMICOLON, glfw.KEY_EQUAL,
    glfw.KEY_LEFT_BRACKET, glfw.KEY_BACKSLASH, glfw.KEY_RIGHT_BRACKET,
    glfw.KEY_GRAVE_ACCENT,
    *range(glfw.KEY_0, glfw.KEY_9 + 1),
})

_MOD_SHORTCUT = glfw.MOD_CONTROL | glfw.MOD_SUPER | glfw.MOD_ALT


def _printable_keysym(key: int) -> int:
    if glfw.KEY_A <= key <= glfw.KEY_Z:
        return ord("a") + (key - glfw.KEY_A)
    if key in _GLFW_PRINTABLE_ASCII:
        return key
    return 0


def key_to_x11(key: int, mods: int = 0) -> int:
    """X11 keysym to put on the RFB wire for a glfw key event.

    Special keys always map. Printable keys map only when Ctrl/Super/Alt
    is held — otherwise `on_char` delivers the layout-correct codepoint
    and mapping here would duplicate or ignore Dvorak/AZERTY.
    Returns 0 if this event should be ignored (bare printable).
    """
    ks = GLFW_KEY_TO_X11.get(key, 0)
    if ks:
        return ks
    if mods & _MOD_SHORTCUT:
        return _printable_keysym(key)
    return 0


def glfw_button_to_rfb_bit(glfw_button: int) -> int:
    """Translate a glfw mouse-button code to Apple's RFB pointer-mask
    bit. Returns 0 for unsupported buttons (extras 4 + 5)."""
    if glfw_button == glfw.MOUSE_BUTTON_LEFT:
        return BTN_LEFT
    if glfw_button == glfw.MOUSE_BUTTON_RIGHT:
        return BTN_RIGHT
    if glfw_button == glfw.MOUSE_BUTTON_MIDDLE:
        return BTN_MIDDLE
    return 0


__all__ = ["GLFW_KEY_TO_X11", "key_to_x11", "glfw_button_to_rfb_bit"]
