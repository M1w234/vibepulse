#!/bin/sh
# Compile-only target for Waveshare ESP32-S3-Touch-AMOLED-1.75C.
# Deliberately contains no flash/monitor action: physical validation starts
# only after the ordered board arrives and passes the vendor-demo gate.
set -eu

repo_root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)

if ! command -v idf.py >/dev/null 2>&1; then
  idf_export=${IDF_EXPORT:-"$HOME/esp/esp-idf/export.sh"}
  if [ ! -f "$idf_export" ]; then
    printf '%s\n' \
      "ESP-IDF is not active and export.sh was not found at: $idf_export" \
      "Install ESP-IDF 5.5, or run with IDF_EXPORT=/absolute/path/export.sh." >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  . "$idf_export" >/dev/null
fi

export TORGET_BOARD=round-1.75c
cd "$repo_root"
exec idf.py -B build-round-1.75c build
