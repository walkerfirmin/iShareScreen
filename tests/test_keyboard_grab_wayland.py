"""Wayland shortcuts-inhibit structs used by the desktop keyboard grab."""
from __future__ import annotations

from isharescreen.frontend.desktop.keyboard_grab import _wl_iface


def test_wl_iface_pins_method_table():
    iface = _wl_iface(
        b"zwp_keyboard_shortcuts_inhibitor_v1", 1,
        [(b"destroy", b"", None)],
    )
    assert iface.name == b"zwp_keyboard_shortcuts_inhibitor_v1"
    assert iface.version == 1
    assert iface.method_count == 1
    assert iface.methods[0].name == b"destroy"
    assert iface.methods[0].signature == b""
    assert iface.event_count == 0
    assert not iface.events


def test_wl_iface_declares_inhibitor_events():
    """Compositor sends active/inactive; event_count=0 kills the GLFW display."""
    iface = _wl_iface(
        b"zwp_keyboard_shortcuts_inhibitor_v1", 1,
        [(b"destroy", b"", None)],
        [(b"active", b"", None), (b"inactive", b"", None)],
    )
    assert iface.event_count == 2
    assert iface.events[0].name == b"active"
    assert iface.events[0].signature == b""
    assert iface.events[1].name == b"inactive"
    assert iface.events[1].signature == b""
