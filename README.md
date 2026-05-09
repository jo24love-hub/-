# Joystick Mouse Controller

Drive your computer's mouse with a regular game controller. The mapping
mirrors the JoyToKey configuration in `screenshots/`:

| Input               | Action                                  |
| ------------------- | --------------------------------------- |
| Left stick          | Move cursor (up/down/left/right, 25 px) |
| Right stick → right | Left click                              |
| Right stick → down  | Right click                             |
| Button 2            | Left click                              |
| Button 3            | Right click                             |

Works on Windows, macOS, and Linux. Any controller that the OS
recognises as a joystick (Xbox, PlayStation, generic USB pads, etc.)
will work.

## Install

```bash
pip install -r requirements.txt
```

On Linux, `pynput` may need an X11 / uinput backend. On macOS you must
grant Accessibility permission to the terminal running the script so it
can move the mouse.

## Run

```bash
python joystick_mouse.py
```

Plug in the controller before launching. Press `Ctrl+C` to stop.

## Tuning

Open `joystick_mouse.py` and adjust the constants near the top:

- `MAX_STEP_PIXELS` — cursor speed at full stick deflection.
- `DEAD_ZONE` — ignore tiny stick movement (drift).
- `STICK_CLICK_THRESHOLD` — how hard the right stick must be pushed to
  register as a click.
- `LEFT_CLICK_BUTTON` / `RIGHT_CLICK_BUTTON` — pygame button indices for
  direct-click buttons (0-indexed; JoyToKey's "Button 2" = index 1).
