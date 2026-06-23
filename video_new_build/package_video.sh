#!/usr/bin/env bash
# package_video.sh <project_dir> <build_script> <config_json> <final_video> <zip_basename>
# Builds description.txt (with auto chapters) and a ZIP containing:
#   final video, all source clips, thumbnail, description.txt
set -e
PROJ="$1"; BUILD="$2"; CFG="$3"; FINAL="$4"; ZIPBASE="$5"
ROOT=/home/user/YT-Clip-Calssifier
cd "$ROOT"
DESC="$PROJ/description.txt"
python3 video_new_build/gen_description.py "$PROJ" "$BUILD" "$CFG" > "$DESC"
echo "wrote $DESC ($(wc -l < "$DESC") lines)"
# staging dir with clean names
STAGE="/tmp/pkg_${ZIPBASE}"; rm -rf "$STAGE"; mkdir -p "$STAGE/source_clips"
cp "$FINAL" "$STAGE/${ZIPBASE}.mp4"
cp "$DESC" "$STAGE/description.txt"
[ -f "$PROJ/thumbnail.png" ] && cp "$PROJ/thumbnail.png" "$STAGE/thumbnail.png"
cp "$PROJ/Source clips/"*.mp4 "$STAGE/source_clips/" 2>/dev/null || true
echo "  source clips: $(ls "$STAGE/source_clips" | wc -l)"
OUT="$ROOT/${ZIPBASE}_DELIVERABLE.zip"
rm -f "$OUT"
( cd "$STAGE" && zip -r -q "$OUT" . )
echo "ZIP: $OUT ($(du -h "$OUT" | cut -f1))"
rm -rf "$STAGE"
