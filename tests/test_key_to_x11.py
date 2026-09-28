"""Modifier-held glfw keys must become RFB X11 keysyms (on_char does not fire)."""
from __future__ import annotations

import glfw

from isharescreen.frontend.desktop.keymap import GLFW_KEY_TO_X11, key_to_x11


def test_special_keys_always_map():
    assert key_to_x11(glfw.KEY_TAB, 0) == 0xff09
    assert key_to_x11(glfw.KEY_LEFT_CONTROL, 0) == 0xffe3
    assert key_to_x11(glfw.KEY_LEFT_SUPER, 0) == 0xffeb
    assert key_to_x11(glfw.KEY_LEFT_ALT, 0) == 0xffe9
    assert key_to_x11(glfw.KEY_TAB, glfw.MOD_ALT) == GLFW_KEY_TO_X11[glfw.KEY_TAB]


def test_bare_printable_left_to_on_char():
    assert key_to_x11(glfw.KEY_C, 0) == 0
    assert key_to_x11(glfw.KEY_MINUS, 0) == 0
    assert key_to_x11(glfw.KEY_SPACE, glfw.MOD_SHIFT) == 0


def test_ctrl_super_alt_synthesize_letters_and_punctuation():
    assert key_to_x11(glfw.KEY_C, glfw.MOD_CONTROL) == ord("c")
    assert key_to_x11(glfw.KEY_C, glfw.MOD_SUPER) == ord("c")
    assert key_to_x11(glfw.KEY_MINUS, glfw.MOD_SUPER) == ord("-")
    assert key_to_x11(glfw.KEY_LEFT_BRACKET, glfw.MOD_CONTROL) == ord("[")
    assert key_to_x11(glfw.KEY_PERIOD, glfw.MOD_ALT) == ord(".")
    assert key_to_x11(glfw.KEY_SPACE, glfw.MOD_CONTROL) == ord(" ")
    assert key_to_x11(glfw.KEY_EQUAL, glfw.MOD_CONTROL | glfw.MOD_SHIFT) == ord("=")
