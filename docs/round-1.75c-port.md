# Round 1.75C port status

Target board: Waveshare ESP32-S3-Touch-AMOLED-1.75C, 466×466 circular AMOLED.

## Ready before the board arrives

- `TORGET_SIM_PROFILE=round-1.75c` creates a true 466×466 simulator window.
- Platform roots and overlays clip to the circular panel.
- VibePulse quota, burn-rate, tracker, GitHub, value, completion, `Needs You`, boot, launcher, and OTA surfaces have round-specific geometry.
- Round-specific raster contracts guard large percentage edge clearance and
  every `Needs You` decision state against copy overlap and curved-edge loss.
- The default `square` simulator remains byte-for-byte identical to the upstream 480×480 capture set.
- `tools/build-round-1.75c.sh` selects the official 1.75C BSP in an isolated
  build directory and dependency lock; it has no flash action.
- The round firmware compiles out the square board's GPIO18 button and
  QMI8658/MADCTL auto-rotation calibration. Touch uses the vendor BSP default
  until it can be measured on the ordered unit.

Build and capture the round profile:

```sh
cmake -S sim -B sim/build-round -G Ninja -DTORGET_SIM_PROFILE=round-1.75c
ninja -C sim/build-round
SDL_VIDEODRIVER=dummy TORGET_CAPTURE_DIR=/tmp/vibepulse-round \
  ./sim/build-round/torget-sim --vibepulse-static-qa
```

Compile the round firmware without flashing:

```sh
./tools/build-round-1.75c.sh
```

## Compile verification

On 2026-08-17, commit `91d16ac` was compiled from scratch in Espressif's
official `espressif/idf:v5.5.2` container for both isolated targets:

- `round-1.75c`: `torget.bin` size `0x1c3630`; 65% of the smallest app
  partition remained free.
- `square-2.16`: `torget.bin` size `0x1c49a0`; 65% of the smallest app
  partition remained free.

This verifies dependency selection and compilation only. It is not evidence of
display, touch, power, Wi-Fi, or other behavior on the physical round board.

## Deliberately not claimed yet

The 1.75C firmware target is compile-only. It must not be called flash-ready
or installed on the ordered board until the hardware-arrival gate below.

The round firmware target currently pins:

- `waveshare/esp32_s3_touch_amoled_1_75c` version `^3.0.0`
- LVGL `9.5.0`
- ESP-IDF `5.5.2` (the BSP manifest accepts ESP-IDF `>=5.5`)

Selecting that dependency is only the first target step. The existing custom
touch transform, QMI8658 orientation calibration, CO5300 MADCTL/gap table,
GPIO18 `KEY3` behavior, power management, brightness, and sleep/wake behavior
were learned on the square board. They are not portable evidence for the round
board and remain disabled or vendor-default work until the device is present.

## Hardware arrival gate

1. Photograph the board/revision and verify it matches the 1.75C documentation.
2. Flash Waveshare's official `02_lvgl_demo_v9` build first; verify display, full-edge touch, brightness, USB, and reset.
3. Build VibePulse against the 1.75C BSP and record boot logs before changing mappings.
4. Calibrate touch and button behavior with a labeled test screen.
5. Run every static state on glass, then test swipe, long-press, `Needs You`, dim/wake, Wi-Fi reconnect, and 30-minute stability.
6. Only after those checks mark the target firmware flash-ready.
