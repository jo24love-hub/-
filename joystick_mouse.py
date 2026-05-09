"""Joystick-to-mouse controller.

Uses a generic game controller / joypad to drive the system mouse,
mimicking the JoyToKey configuration shown in the project screenshots:

    Stick 1 (left stick):  cursor movement (X/Y, speed 25)
    Stick 2 (right stick): right  -> left click
                           down   -> right click
    Buttons:               Button 2 -> left click
                           Button 3 -> right click

Cross-platform: works on Windows, macOS, and Linux as long as a
joystick is recognised by SDL/pygame.
"""

from __future__ import annotations

import sys
import time

import pygame
from pynput.mouse import Button, Controller


# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------

# Maximum cursor movement, in pixels, per polling tick when a stick is
# pushed fully. Matches the "25" value that JoyToKey uses in the
# screenshots (커서 이동 = 25).
MAX_STEP_PIXELS = 25

# Anything below this magnitude on a stick axis is treated as zero,
# to suppress controller drift.
DEAD_ZONE = 0.18

# How often (seconds) we poll the joystick and move the mouse.
# 60 Hz feels smooth without burning CPU.
TICK_SECONDS = 1.0 / 60.0

# Stick / button indices. SDL exposes axes as floats in [-1, 1].
# These are the conventional mappings for an XInput-style pad; most
# generic pads on Windows/Mac/Linux line up the same way.
LEFT_STICK_X = 0
LEFT_STICK_Y = 1
RIGHT_STICK_X = 2
RIGHT_STICK_Y = 3

# Click-on-stick threshold: how far stick 2 must be pushed before it
# counts as a "click" press (matches the JoyToKey behaviour where the
# stick direction itself triggers the click).
STICK_CLICK_THRESHOLD = 0.6

# Button indices used for direct clicks.  pygame numbers buttons from 0,
# so "Button 2" in JoyToKey is index 1, "Button 3" is index 2.
LEFT_CLICK_BUTTON = 1
RIGHT_CLICK_BUTTON = 2


# ---------------------------------------------------------------------------
# Controller plumbing
# ---------------------------------------------------------------------------


def _apply_dead_zone(value: float) -> float:
    if abs(value) < DEAD_ZONE:
        return 0.0
    # Re-scale so the live region still spans [-1, 1] after the dead zone.
    sign = 1.0 if value > 0 else -1.0
    return sign * (abs(value) - DEAD_ZONE) / (1.0 - DEAD_ZONE)


def _open_first_joystick() -> pygame.joystick.JoystickType:
    pygame.init()
    pygame.joystick.init()

    count = pygame.joystick.get_count()
    if count == 0:
        print("No joystick detected. Plug in a controller and try again.")
        sys.exit(1)

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Using joystick: {joystick.get_name()}")
    print(f"  axes={joystick.get_numaxes()}  buttons={joystick.get_numbuttons()}")
    return joystick


def _axis(joystick: pygame.joystick.JoystickType, index: int) -> float:
    if index >= joystick.get_numaxes():
        return 0.0
    return _apply_dead_zone(joystick.get_axis(index))


def _button(joystick: pygame.joystick.JoystickType, index: int) -> bool:
    if index >= joystick.get_numbuttons():
        return False
    return bool(joystick.get_button(index))


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def run() -> None:
    joystick = _open_first_joystick()
    mouse = Controller()

    # Track click state so we only press/release on edges.
    left_down = False
    right_down = False

    print("Joystick mouse running. Press Ctrl+C to quit.")
    try:
        while True:
            pygame.event.pump()

            # --- Cursor movement (left stick) --------------------------------
            dx = _axis(joystick, LEFT_STICK_X) * MAX_STEP_PIXELS
            dy = _axis(joystick, LEFT_STICK_Y) * MAX_STEP_PIXELS
            if dx or dy:
                mouse.move(int(round(dx)), int(round(dy)))

            # --- Clicks ------------------------------------------------------
            # Right stick pushed right  -> left click
            # Right stick pushed down   -> right click
            stick2_x = _axis(joystick, RIGHT_STICK_X)
            stick2_y = _axis(joystick, RIGHT_STICK_Y)

            want_left = (
                stick2_x > STICK_CLICK_THRESHOLD
                or _button(joystick, LEFT_CLICK_BUTTON)
            )
            want_right = (
                stick2_y > STICK_CLICK_THRESHOLD
                or _button(joystick, RIGHT_CLICK_BUTTON)
            )

            if want_left and not left_down:
                mouse.press(Button.left)
                left_down = True
            elif not want_left and left_down:
                mouse.release(Button.left)
                left_down = False

            if want_right and not right_down:
                mouse.press(Button.right)
                right_down = True
            elif not want_right and right_down:
                mouse.release(Button.right)
                right_down = False

            time.sleep(TICK_SECONDS)
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        if left_down:
            mouse.release(Button.left)
        if right_down:
            mouse.release(Button.right)
        pygame.quit()


if __name__ == "__main__":
    run()
