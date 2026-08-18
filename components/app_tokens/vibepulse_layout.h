#ifndef VIBEPULSE_LAYOUT_H
#define VIBEPULSE_LAYOUT_H

#include "torget_display.h"
#include "vibepulse_layout.generated.h"

/* The generated header is the approved 480x480 Studio source of truth. The
 * round profile overrides geometry only; typography and palette remain the
 * same product language. A round Studio export can replace these overrides
 * once the physical-panel review is complete. */
#if TORGET_DISPLAY_ROUND
#undef VP_SCREEN_W
#undef VP_SCREEN_H
#undef VP_SAFE_X
#undef VP_CONTENT_W
#undef VP_PROVIDER_Y
#undef VP_QUOTA_Y
#undef VP_PERCENT_Y
#undef VP_BAR_Y
#undef VP_RESET_Y
#undef VP_STATUS_Y
#undef VP_STATUS_H

#define VP_SCREEN_W TORGET_DISPLAY_WIDTH
#define VP_SCREEN_H TORGET_DISPLAY_HEIGHT
#define VP_SAFE_X 50
#define VP_CONTENT_W 366
#define VP_PROVIDER_Y 48
#define VP_QUOTA_Y 94
#define VP_PERCENT_Y 126
#define VP_BAR_Y 300
#define VP_RESET_Y 344
#define VP_STATUS_Y 386
#define VP_STATUS_H 52
#endif

#endif
