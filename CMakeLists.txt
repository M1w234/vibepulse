# Torget — ESP-IDF-projektet för skärmplattformen. Bygg (efter
# `. ~/esp/esp-idf/export.sh`):
#   idf.py set-target esp32s3 && idf.py build
#   idf.py -p /dev/cu.usbmodem* flash monitor
#
# Simulatorn under sim/ är ett HELT eget CMake-projekt och byggs som förr.
# Det som delas mellan dem är platform/, components/app_* (utom net.c) och
# kärnkomponenterna — samma kod på Macen som på hyllan, per design.
cmake_minimum_required(VERSION 3.16)

# One source tree, two explicit hardware targets. The square target remains the
# default so an existing `idf.py build` cannot silently change boards. The
# round target is selected by tools/build-round-1.75c.sh, gets its own managed-
# dependency lock, and compiles out every square-only physical calibration.
set(_TORGET_BOARD_DEFAULT "square-2.16")
if(DEFINED ENV{TORGET_BOARD} AND NOT "$ENV{TORGET_BOARD}" STREQUAL "")
  set(_TORGET_BOARD_DEFAULT "$ENV{TORGET_BOARD}")
endif()
set(TORGET_BOARD "${_TORGET_BOARD_DEFAULT}" CACHE STRING
    "Hardware target: square-2.16 or round-1.75c")
set_property(CACHE TORGET_BOARD PROPERTY STRINGS square-2.16 round-1.75c)
if(NOT TORGET_BOARD STREQUAL "square-2.16" AND
   NOT TORGET_BOARD STREQUAL "round-1.75c")
  message(FATAL_ERROR
    "Unknown TORGET_BOARD='${TORGET_BOARD}' (use square-2.16 or round-1.75c)")
endif()
# The component manifest is evaluated during early expansion and can only see
# environment variables, not this cache variable.
set(ENV{TORGET_BOARD} "${TORGET_BOARD}")
# third_party/ innehåller vendrade komponenter (cjson) som apparna delar.
# Vibbe (app_buddy) bor i sitt eget repo (~/Buddy) och delas in härifrån —
# EN källa, ingen kopiedrift (inflyttsbeslutet 2026-08-07: "alla tre ska bo
# där"). Utan ~/Buddy (en färsk klon utifrån) byggs plattformen med två
# appar — registry.c grindas på TORGET_HAVE_BUDDY.
set(EXTRA_COMPONENT_DIRS third_party)

# Vibbe kräver UTTRYCKLIG avsikt sedan frysjakten 2026-08-14: dess ljud- och
# USB-stack äter av samma interna DMA-minne som panelflushen lever på, och
# med OTA-grundens ~12 kB extra bootlast föll största sammanhängande
# DMA-block under flushens 11 520 B — varje flush dog i NO_MEM och glaset
# frös på sista bilden medan resten av systemet levde vidare (obducerat via
# seriekonsolen: co5300 "send color data failed" i evig följd). Dessutom
# gömde TinyUSB konsolen exakt när den behövdes. Vibbe siktar på egen
# hårdvara; på VibePulse-panelen byggs den bara in med -DTORGET_WITH_BUDDY=ON
# och en medvetet omprövad minnesbudget.
option(TORGET_WITH_BUDDY "Bygg in Vibbe/Buddy (kräver ~/Buddy och medveten minnesbudget)" OFF)

# Companion-appar bor i sina EGNA repon och är inte del av det här bygget om
# de inte finns utcheckade. En färsk klon utifrån bygger bara VibePulse —
# ingen ska få Solelkollen eller Vibbe på skärmen utan att ha bett om det.
# Sökvägarna kan pekas om med -DTORGET_SOLELKOLLEN_DIR / -DTORGET_BUDDY_DIR.
set(TORGET_SOLELKOLLEN_DIR "$ENV{HOME}/Solelkollen/components"
    CACHE PATH "Companion-katalog för Solelkollen")
set(TORGET_BUDDY_DIR "$ENV{HOME}/Buddy/components"
    CACHE PATH "Companion-katalog för Vibbe/Buddy")

# main/CMakeLists.txt måste läsa dessa i ESP-IDF:s early-expansion (där
# REQUIRES bestäms). Dit når varken cache- eller normalvariabler härifrån —
# bara miljön överlever. Spegla de UPPLÖSTA värdena (inkl. ev. -D-override) till
# miljön så att main grindar sitt REQUIRES på exakt samma sökväg som grindar
# EXTRA_COMPONENT_DIRS nedan. Utan detta sätts TORGET_HAVE_* men komponentens
# include-katalog dras aldrig in, och registry.c faller på app_solelkollen.h.
if(TORGET_BOARD STREQUAL "round-1.75c")
  # The first round firmware is intentionally VibePulse-only. Companion apps
  # have not had their full-screen surfaces reviewed for this physical circle.
  set(ENV{TORGET_SOLELKOLLEN_DIR} "")
else()
  set(ENV{TORGET_SOLELKOLLEN_DIR} "${TORGET_SOLELKOLLEN_DIR}")
endif()
# Tom spegel när Vibbe är bortvald: main/ grindar på $ENV{}-sökvägen, och en
# tom sträng gör båda expansionspassen eniga om att Buddy inte finns — även
# om skalet råkar ha TORGET_BUDDY_DIR exporterad sedan tidigare.
if(TORGET_WITH_BUDDY)
  set(ENV{TORGET_BUDDY_DIR} "${TORGET_BUDDY_DIR}")
else()
  set(ENV{TORGET_BUDDY_DIR} "")
endif()

if(NOT TORGET_BOARD STREQUAL "round-1.75c" AND
   EXISTS "${TORGET_SOLELKOLLEN_DIR}/app_solelkollen")
  list(APPEND EXTRA_COMPONENT_DIRS "${TORGET_SOLELKOLLEN_DIR}")
else()
  message(STATUS "Torget: Solelkollen saknas — bygger utan den (companion-app)")
endif()
if(TORGET_WITH_BUDDY AND EXISTS "${TORGET_BUDDY_DIR}/app_buddy")
  list(APPEND EXTRA_COMPONENT_DIRS "${TORGET_BUDDY_DIR}")
elseif(TORGET_WITH_BUDDY)
  message(STATUS "Torget: TORGET_WITH_BUDDY=ON men ~/Buddy saknas — bygger utan Vibbe/Buddy")
else()
  message(STATUS "Torget: Vibbe/Buddy är bortvald (TORGET_WITH_BUDDY=OFF, frysläxan 2026-08-14)")
endif()
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Conditional manifests need independent locks or alternating target builds
# rewrite one another's dependency graph. Espressif documents this build
# property specifically for multi-target projects.
if(TORGET_BOARD STREQUAL "round-1.75c")
  idf_build_set_property(
    DEPENDENCIES_LOCK
    "${CMAKE_CURRENT_SOURCE_DIR}/dependencies.lock.round-1.75c")
  idf_build_set_property(COMPILE_DEFINITIONS
    "TORGET_BOARD_ROUND_1_75C=1;TORGET_DISPLAY_WIDTH=466;TORGET_DISPLAY_HEIGHT=466;TORGET_DISPLAY_ROUND=1"
    APPEND)
endif()
project(torget)

# LVGL:s minnespool till PSRAM (frysfix 2026-08-16, se docs/lessons.md och
# main/lv_psram_pool.c). LVGL:s inbyggda allokator lägger annars sin
# LV_MEM_SIZE-pool i internt BSS; på panelen tryckte det största
# sammanhängande DMA-blocket under panelflushens 11 520 B → flushen dog i
# NO_MEM och glaset frös (samma klass som frysläxan 2026-08-14, men annan
# svältkälla). Vi ber LVGL ta poolen ur PSRAM via LV_MEM_POOL_ALLOC; det
# interna heapet får då tillbaka ~poolens storlek som sammanhängande block.
# lv_psram_pool.h/.c bor i main/ (därav include-katalogen); symbolen löses i
# den gemensamma länkgruppen.
# Bara en OBJEKT-lik include-def (CMake släpper funktionslika -D:n); själva
# LV_MEM_POOL_ALLOC-makrot bor i main/lv_psram_pool.h och pekar mot
# heap_caps_malloc (PSRAM + 8BIT, INTE DMA — se headern). Include-katalogen gör
# att lvgl-komponenten hittar headern.
idf_component_get_property(lvgl_lib lvgl__lvgl COMPONENT_LIB)
target_compile_definitions(${lvgl_lib} PRIVATE
  "LV_MEM_POOL_INCLUDE=\"lv_psram_pool.h\"")
target_include_directories(${lvgl_lib} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/main")
