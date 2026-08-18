#ifndef TORGET_DISPLAY_H
#define TORGET_DISPLAY_H

#include "lvgl.h"

/* The square board remains the default target. Alternate boards opt in with
 * compile definitions so upstream builds and approved 480x480 rasters do not
 * move merely because another simulator profile exists. */
#ifndef TORGET_DISPLAY_WIDTH
#define TORGET_DISPLAY_WIDTH 480
#endif

#ifndef TORGET_DISPLAY_HEIGHT
#define TORGET_DISPLAY_HEIGHT 480
#endif

#ifndef TORGET_DISPLAY_ROUND
#define TORGET_DISPLAY_ROUND 0
#endif

#define TORGET_DISPLAY_CENTER_X (TORGET_DISPLAY_WIDTH / 2)
#define TORGET_DISPLAY_CENTER_Y (TORGET_DISPLAY_HEIGHT / 2)

static inline void torget_display_clip(lv_obj_t *object) {
#if TORGET_DISPLAY_ROUND
  lv_obj_set_style_radius(object, LV_RADIUS_CIRCLE, 0);
  lv_obj_set_style_clip_corner(object, true, 0);
#else
  (void)object;
#endif
}

#endif
