# iShareScreen setup — this machine

This guide is for the viewer laptop that already has the repo at
`/home/admin/git/iShareScreen`. It is written against the hardware and
packages that were on the box when the doc was created, not a generic
Ubuntu install.

Nothing extra goes on the Mac you want to view. Only this Linux
machine needs `iss`.

## What this machine is

| Item | Value |
|---|---|
| Distro | Pop!_OS 24.04 LTS (Ubuntu noble) |
| Desktop | COSMIC on Wayland (`WAYLAND_DISPLAY=wayland-1`) |
| User | `admin` (`~/.local/bin` is already on `PATH`) |
| Hostname / LAN | `pop-os` — `wlp4s0` at `192.168.1.166/24` |
| Display | built-in `eDP-1` **1920×1200 @ 165 Hz**, scale **100%** (not Retina) |
| dGPU | NVIDIA GeForce RTX 5070 Laptop, driver **595.84** (Vulkan ICD present) |
| iGPU | AMD Phoenix3 (`card0` / `renderD128`, Mesa 26.1 VA-API + Vulkan) |
| Python | `/usr/bin/python3` **3.12.3** |
| Browser | Firefox **153** |
| Repo | `/home/admin/git/iShareScreen` on `main` |

`iss` is **not** installed yet. There is no venv, no `pip`, and no
`python3-venv` / `ensurepip`. The GPU stack (NVIDIA 595, Mesa Vulkan,
`libvulkan1`, `libgl1`, `libegl1`, X11 client libs) is already there.

## What you still need to install

Missing packages that `iss` actually uses:

| Package | Why |
|---|---|
| `python3-venv` | Debian splits `ensurepip` out of the base `python3` package. Without this, `python3 -m venv` fails. |
| `libportaudio2` | audio playback (`sounddevice`) |
| `libfdk-aac2` | AAC-ELD-SBR (Apple PT=101). Video works without it; audio is silently skipped. |
| `wl-clipboard` | clipboard sync on COSMIC/Wayland. `xclip` will not see the COSMIC clipboard. |

Optional, only for debugging GPU decode:

```sh
sudo apt install vulkan-tools vainfo
```

`ufw` is **active**. You may need a rule for inbound UDP 5900–5901 if
the Mac stream never starts after TCP connect succeeds (see
[Firewall](#firewall)).

## 1. Host Mac (no software)

On the Mac you want to view:

1. Recent macOS with Screen Sharing High Performance mode (Apple
   Silicon).
2. **System Settings → General → Sharing → Screen Sharing** → on.
3. Note the Mac’s hostname or LAN IP, plus a local username/password.

Do not install iShareScreen on the Mac. Apple’s `screensharingd` is
the server.

The two machines must reach each other on:

- TCP **5900** (control)
- UDP **5900** (audio + RTCP)
- UDP **5901** (video)

Same `192.168.1.0/24` LAN is the easy case.

## 2. System packages on Pop!_OS

```sh
sudo apt update
sudo apt install python3-venv \
    libportaudio2 libfdk-aac2 \
    wl-clipboard
```

Already present, so you can skip them: `libvulkan1`, `libgl1`,
`libegl1`, `libxrandr2`, `libxinerama1`, `libxcursor1`, `libxi6`,
`mesa-vulkan-drivers`, `mesa-va-drivers`, `nvidia-driver-595`,
`libnvidia-decode-595`.

## 3. Install `iss` from this clone

Use a venv. Ubuntu’s system Python will refuse a global `pip install`.

```sh
mkdir -p ~/.venvs
python3 -m venv ~/.venvs/iss
~/.venvs/iss/bin/pip install -U pip
~/.venvs/iss/bin/pip install -e /home/admin/git/iShareScreen
```

`-e` installs the tree you already have, so local edits show up
without reinstalling. To pin a released checkout instead:

```sh
~/.venvs/iss/bin/pip install /home/admin/git/iShareScreen
```

Put `iss` on your existing user `PATH`:

```sh
mkdir -p ~/.local/bin
ln -sf ~/.venvs/iss/bin/iss ~/.local/bin/iss
hash -r
iss --version
```

Sanity-check decoders (needs the venv’s `av` / PyAV, so run this
*after* the pip install):

```sh
iss --list-decoders
```

On this laptop you want to see `libav-hevc444` (CUDA and/or VAAPI)
and `libav-avc420`. If HEVC 4:4:4 hardware probe fails, `--codec auto`
on the desktop frontend falls back to H.264 — that is still usable.

## 4. First connect

### Interactive (default)

```sh
iss
```

Opens a local browser form (Firefox is fine) for host / user /
password / resolution. On submit it launches the session. Last-used
values (never the password) are stored in `~/.iss/last.json`.

The form is only the control surface. Video opens either:

- **browser** (default) — a second tab via WebTransport on
  `https://127.0.0.1:4433`, H.264 pass-through to WebCodecs, or
- **desktop** — a native wgpu/glfw window.

### Command line

```sh
iss --host mac.local -u youruser
# password prompted; not accepted as an argv flag on purpose
```

Unattended:

```sh
echo "$PASSWORD" | iss --host mac.local -u youruser --password-stdin
```

This laptop’s panel is 1920×1200 at 1×, so a good first advertise is
the default `auto`, or pin it:

```sh
iss --host mac.local -u youruser --advertise 1920x1200 --hidpi off
```

`--hidpi off` (or `auto` on this 100% panel) keeps the Mac UI at 1×.
`--hidpi on` requests a 2× Retina backing (~4× the pixels) and is
usually the wrong choice on this display.

## 5. Connect to 192.168.1.113

This LAN Mac (`admin` on `192.168.1.113`). `--host` always needs
`--password-stdin`. That flag takes **no argument** — `iss` then
prompts `password:` (hidden). Do not put the password on the command
line (it becomes an unrecognized argument and shows up in `ps`).

Optional reachability check:

```sh
ping 192.168.1.113
```

Connect (browser viewer):

```sh
iss --host 192.168.1.113 -u admin --password-stdin
```

Type the password at the prompt, then open **http://localhost:4433/**.
Click the tab once if the picture is gray (wakes WebCodecs / the audio
context).

Native window instead:

```sh
iss --host 192.168.1.113 -u admin --password-stdin --frontend desktop
```

Or run plain `iss` (no `--host`) for the browser connect form.

## 6. Which frontend on COSMIC

**Browser (default)** is the path of least resistance here: Firefox
153 is already installed, COSMIC/Wayland windowing is not involved in
the video surface, and the codec is H.264 (hardware-decodes everywhere).

```sh
iss --host mac.local -u youruser --frontend browser
```

Accept the self-signed WebTransport cert warning once. Chrome/Edge
also work if you add one later; Firefox does not need
`--trust-cert-for-safari`.

**Desktop** is the lower-latency native viewer (HEVC 4:4:4 when the
RTX 5070 probe succeeds):

```sh
iss --host 192.168.1.113 -u admin --password-stdin --frontend desktop
```

This laptop’s glfw wheel is native **Wayland** (not XWayland). While
the viewer is focused, iss asks COSMIC to inhibit compositor shortcuts
(`zwp_keyboard_shortcuts_inhibit_v1`) so Super (Mac Cmd), Alt+Tab,
Ctrl+C, and punctuation combos (Ctrl+`[`, Cmd+`-`, …) go to the Mac
instead of the desktop. Look for `keyboard grab acquired (Wayland
shortcuts-inhibit)` in the log. Click the window first. Do **not** set
`ISS_CTRL_AS_CMD` unless you want Linux Ctrl rewritten as Mac Cmd. If a
COSMIC permission toast appears, allow it. Opt out of the grab with
`ISS_GRAB_KEYBOARD=0`.

If the window is blank or never appears, try forcing X11 glfw (you
lose compositor shortcut pass-through):

```sh
PYGLFW_LIBRARY_VARIANT=x11 iss --host 192.168.1.113 -u admin --password-stdin --frontend desktop
```

Hybrid GPU: wgpu should pick the NVIDIA Vulkan ICD
(`/usr/share/vulkan/icd.d/nvidia_icd.json`). To force NVIDIA:

```sh
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json
iss --host mac.local -u youruser --frontend desktop
```

To force the AMD iGPU instead:

```sh
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.json
```

## 7. Audio, clipboard, curtain

- **Audio** — install `libfdk-aac2` (step 2). Without it, video still
  works. Disable on purpose with `--no-audio`.
- **Clipboard** — `wl-clipboard` on this desktop. COSMIC is not
  GNOME, so GPaste is not used. If sync is silent, confirm
  `wl-copy` / `wl-paste` work in a terminal.
- **Curtain** (default on) — blanks the Mac’s physical screen and
  encodes a virtual display. Use `--no-curtain` to mirror whatever is
  on the Mac’s panel (useful if the virtual display never starts
  sending RTP).

If someone else is logged in at the Mac’s console, `iss` will share
that session (the Mac user gets a consent popup) unless you pass
`--alt-session` for a separate virtual desktop.

## 8. Firewall

`iss` sends from UDP 5900–5901 during connect. If TCP works but the
picture never appears, allow the return path on **this** laptop:

```sh
sudo ufw allow 5900:5901/udp comment 'iss Apple Screen Sharing media'
sudo ufw status
```

The Mac’s Screen Sharing service must also be allowed on its side
(System Settings → Network → Firewall, or just leave Screen Sharing
enabled — macOS opens those ports with the service).

## 9. Useful commands

```sh
# capability matrix for this GPU
iss --list-decoders

# protocol smoke test, no window (10–30 s)
echo "$PASSWORD" | iss --headless --host mac.local -u youruser \
    --password-stdin --auto-quit-secs 15

# native window, HEVC if the 5070 probe passes
iss --host mac.local -u youruser --frontend desktop --codec auto

# force H.264 (same as the browser path)
iss --host mac.local -u youruser --frontend desktop --codec avc

# capture a session for the bundled dissector
iss --host mac.local -u youruser --record /tmp/iss-session.pcap
```

Live-session keys (desktop / dashboard): **f** force IDR refresh,
**r** reconnect, **d** disconnect, **q** quit.

## 10. If something fails

| Symptom | Likely cause on this box |
|---|---|
| `python3 -m venv` errors about `ensurepip` | `python3-venv` not installed (step 2). |
| `iss: command not found` | symlink missing; run `~/.venvs/iss/bin/iss` or redo the `~/.local/bin` link. |
| TCP “actively rejected” | Screen Sharing off on the Mac, or wrong IP/port. |
| Connected, 0 RTP / gray window | host encoder stall, IPv6-only hostname, or UDP blocked. Try the Mac’s IPv4 (`192.168.1.x`), `--no-curtain`, toggle Screen Sharing off/on, then [Firewall](#firewall). |
| Video yes, audio no | `libfdk-aac2` missing. |
| Clipboard does not sync | install `wl-clipboard`; `xclip` is the wrong helper on COSMIC. |
| Desktop window blank | XWayland/Vulkan ICD; try the `VK_ICD_FILENAMES` / `GDK_BACKEND=x11` exports above. |
| Browser tab will not connect to `:4433` | another process owns 4433 (`--bridge-port 4434`) or the cert prompt was dismissed. |

## 11. After a `git pull`

```sh
~/.venvs/iss/bin/pip install -e /home/admin/git/iShareScreen
```

Re-run `iss --list-decoders` if decode behavior changes; the registry
probes this machine at runtime.
