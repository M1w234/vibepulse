from pathlib import Path


root = Path(__file__).resolve().parents[1]
display = (root / "platform/torget_display.h").read_text(encoding="utf-8")
layout = (root / "components/app_tokens/vibepulse_layout.h").read_text(
    encoding="utf-8"
)
sim_cmake = (root / "sim/CMakeLists.txt").read_text(encoding="utf-8")
sim_main = (root / "sim/main.c").read_text(encoding="utf-8")
platform_ui = (root / "platform/torget_ui.c").read_text(encoding="utf-8")
generated = (
    root / "components/app_tokens/vibepulse_layout.generated.h"
).read_text(encoding="utf-8")

# The approved square profile remains the fallback and its generated Studio
# geometry is untouched.
assert "#define TORGET_DISPLAY_WIDTH 480" in display
assert "#define TORGET_DISPLAY_HEIGHT 480" in display
assert "#define VP_SCREEN_W 480" in generated
assert "#define VP_SCREEN_H 480" in generated
assert "#define VP_SAFE_X 22" in generated
assert "#define VP_CONTENT_W 436" in generated

# The round simulator is explicit, exact-size, and cannot silently accept a
# misspelled profile.
for required in (
    'set(TORGET_SIM_PROFILE "square"',
    'TORGET_SIM_PROFILE STREQUAL "round-1.75c"',
    "TORGET_DISPLAY_WIDTH=466",
    "TORGET_DISPLAY_HEIGHT=466",
    "TORGET_DISPLAY_ROUND=1",
    "Unknown TORGET_SIM_PROFILE",
):
    assert required in sim_cmake, f"missing round simulator contract: {required}"

assert "lv_sdl_window_create(TORGET_DISPLAY_WIDTH," in sim_main
assert "TORGET_DISPLAY_HEIGHT);" in sim_main
assert 'dump_frame("launcher-round")' in sim_main

# Round geometry is an override around the generated square source, not a
# rewrite of it. The screen and content roots must clip to the physical circle.
for required in (
    "#if TORGET_DISPLAY_ROUND",
    "#define VP_SCREEN_W TORGET_DISPLAY_WIDTH",
    "#define VP_SCREEN_H TORGET_DISPLAY_HEIGHT",
    "#define VP_SAFE_X 50",
    "#define VP_CONTENT_W 366",
):
    assert required in layout, f"missing round layout rule: {required}"

assert "LV_RADIUS_CIRCLE" in display
assert "lv_obj_set_style_clip_corner(object, true, 0);" in display
assert platform_ui.count("torget_display_clip(") >= 3

print("round display profile wiring: OK")
