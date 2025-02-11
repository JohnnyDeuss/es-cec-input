#!/usr/bin/env python3
"""
Name: es-cec-input.py
Version: 1.5
Description: cec remote control for emulation station in retropie
Author: dillbyrne
Homepage: https://github.com/dillbyrne/es-cec-input
Licence: GPL3

It depends on python-uinput package which contains
the library and the udev rules at
/etc/udev/rules.d/40-uinput.rules

cec-utils also needs to be installed

to run the code as a non root user
sudo addgroup uinput
sudo adduser pi uinput

to start on boot, add to user crontab. crontab -e
@reboot hohup ./home/pi/RetroPie/scripts/es-cec-input.py
"""

import asyncio
import subprocess
import sys

import uinput


def get_keymap():
    """Map ES supported keys to python-uinput keys."""

    keymap = {
        "left": uinput.KEY_LEFT,
        "right": uinput.KEY_RIGHT,
        "up": uinput.KEY_UP,
        "down": uinput.KEY_DOWN,
        "enter": uinput.KEY_ENTER,
        "kp_enter": uinput.KEY_KPENTER,
        "tab": uinput.KEY_TAB,
        "insert": uinput.KEY_INSERT,
        "del": uinput.KEY_DELETE,
        "end": uinput.KEY_END,
        "home": uinput.KEY_HOME,
        "rshift": uinput.KEY_RIGHTSHIFT,
        "shift": uinput.KEY_LEFTSHIFT,
        "rctrl": uinput.KEY_RIGHTCTRL,
        "ctrl": uinput.KEY_LEFTCTRL,
        "ralt": uinput.KEY_RIGHTALT,
        "alt": uinput.KEY_LEFTALT,
        "space": uinput.KEY_SPACE,
        "escape": uinput.KEY_ESC,
        "kp_minus": uinput.KEY_KPMINUS,
        "kp_plus": uinput.KEY_KPPLUS,
        "f1": uinput.KEY_F1,
        "f2": uinput.KEY_F2,
        "f3": uinput.KEY_F3,
        "f4": uinput.KEY_F4,
        "f5": uinput.KEY_F5,
        "f6": uinput.KEY_F6,
        "f7": uinput.KEY_F7,
        "f8": uinput.KEY_F8,
        "f9": uinput.KEY_F9,
        "f10": uinput.KEY_F10,
        "f11": uinput.KEY_F11,
        "f12": uinput.KEY_F12,
        "num1": uinput.KEY_1,
        "num2": uinput.KEY_2,
        "num3": uinput.KEY_3,
        "num4": uinput.KEY_4,
        "num5": uinput.KEY_5,
        "num6": uinput.KEY_6,
        "num7": uinput.KEY_7,
        "num8": uinput.KEY_8,
        "num9": uinput.KEY_9,
        "num0": uinput.KEY_0,
        "pageup": uinput.KEY_PAGEUP,
        "pagedown": uinput.KEY_PAGEDOWN,
        "keypad1": uinput.KEY_KP1,
        "keypad2": uinput.KEY_KP2,
        "keypad3": uinput.KEY_KP3,
        "keypad4": uinput.KEY_KP4,
        "keypad5": uinput.KEY_KP5,
        "keypad6": uinput.KEY_KP6,
        "keypad7": uinput.KEY_KP7,
        "keypad8": uinput.KEY_KP8,
        "keypad9": uinput.KEY_KP9,
        "keypad0": uinput.KEY_KP0,
        "period": uinput.KEY_DOT,
        "capslock": uinput.KEY_CAPSLOCK,
        "numlock": uinput.KEY_NUMLOCK,
        "backspace": uinput.KEY_BACKSPACE,
        "pause": uinput.KEY_PAUSE,
        "scrolllock": uinput.KEY_SCROLLLOCK,
        "backquote": uinput.KEY_GRAVE,
        "comma": uinput.KEY_COMMA,
        "minus": uinput.KEY_MINUS,
        "slash": uinput.KEY_SLASH,
        "semicolon": uinput.KEY_SEMICOLON,
        "equals": uinput.KEY_EQUAL,
        "backslash": uinput.KEY_BACKSLASH,
        "kp_period": uinput.KEY_KPDOT,
        "kp_equals": uinput.KEY_KPEQUAL,
        "a": uinput.KEY_A,
        "b": uinput.KEY_B,
        "c": uinput.KEY_C,
        "d": uinput.KEY_D,
        "e": uinput.KEY_E,
        "f": uinput.KEY_F,
        "g": uinput.KEY_G,
        "h": uinput.KEY_H,
        "i": uinput.KEY_I,
        "j": uinput.KEY_J,
        "k": uinput.KEY_K,
        "l": uinput.KEY_L,
        "m": uinput.KEY_M,
        "n": uinput.KEY_N,
        "o": uinput.KEY_O,
        "p": uinput.KEY_P,
        "q": uinput.KEY_Q,
        "r": uinput.KEY_R,
        "s": uinput.KEY_S,
        "t": uinput.KEY_T,
        "u": uinput.KEY_U,
        "v": uinput.KEY_V,
        "w": uinput.KEY_W,
        "x": uinput.KEY_X,
        "y": uinput.KEY_Y,
        "z": uinput.KEY_Z,
    }

    return keymap


def generate_keylist():
    """
    Generate a list of keys we actually need. This will be stored in memory and
    will comprise of a, b, x, y, start, select, l, r, left, right, up, down,
    l2, r2, l3 and r3 keyboard corresponding values the user has chosen in the
    retroarch.cfg file.
    """

    keylist = []
    key_bindings = get_key_bindings("/opt/retropie/configs/all/retroarch.cfg")
    keymap = get_keymap()
    errors = []

    for binding in key_bindings:

        try:
            keylist.append(keymap[binding])
        except KeyError as e:
            errors.append(e)

    if errors:
        print(
            f"The {', '.join(errors)} keys in your retroarch.cfg are "
            "unsupported by this script\n"
        )
        print("Supported keys are:\n")
        print(get_keymap().keys())
        sys.exit()

    return keylist


def get_key_bindings(ra_cfg):
    """Read key mappings from retroarch.cfg file."""

    keys = []
    with open(ra_cfg) as fp:
        for line in fp:
            if (
                "input_player1_" in line
                and "#" not in line
                and "_analog_dpad_mode" not in line
            ):
                keys.append(line.split("=")[1][2:-2])
    return keys


def register_device(keylist):
    return uinput.Device(keylist)


def parse_cec_line(line, keylist):
    """
    Emulate keyboard presses when a mapped button on the remote control has
    been pressed.

    To navigate ES, only a, b, start, select, up, down, left and right are
    required.
    """
    line = line.decode()
    if "released" in line:
        # Select
        if "rewind" in line or "yellow" in line:
            return keylist[5]
        # Start
        elif "Fast forward" in line or "blue" in line:
            return keylist[4]
        # Left on DPAD
        elif "left" in line:
            return keylist[8]
        # Right on DPAD
        elif "right" in line:
            return keylist[9]
        # Up on DPAD
        elif "up" in line:
            return keylist[10]
        # Down on DPAD
        elif "down" in line:
            return keylist[11]
        # A Button
        elif "select" in line or "red" in line:
            return keylist[0]
        # B Button
        elif "exit" in line or "green" in line:
            return keylist[1]
    return None


excluded_processes = [
    "kodi_v7.bin",
    "kodi.bin_v7",
    "retroarch",
    "reicast",
    "drastic",
]


def in_excluded_process():
    """Check if a process is running for which we want CEC to be disabled."""
    running_processes = subprocess.check_output(["ps", "-A"]).decode()
    return any(
        excluded_process in running_processes
        for excluded_process in excluded_processes
    )


async def main():
    keylist = generate_keylist()
    device = register_device(keylist)

    proc = await asyncio.create_subprocess_shell(
        "cec-client", stdout=asyncio.subprocess.PIPE
    )

    while True:
        line = await proc.stdout.readline()
        key = parse_cec_line(line, keylist)
        if key is not None and not in_excluded_process():
            device.emit_click(key)


if __name__ == "__main__":
    asyncio.run(main())
