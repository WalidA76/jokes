#!/bin/sh
# usage: ./mux_voiceover.sh voice.(mp3|wav) [out.mp4]
# Mixes your recorded voice-over (timed from 0s, see VO_script_AR.md) with the SFX-only track. No music.
VO="$1"; OUT="${2:-output/ChatGPT_Photo_Edit_Reel_VO_SFX.mp4}"
ffmpeg -y -i output/ChatGPT_Photo_Edit_Reel_SFX_only.mp4 -i "$VO" -filter_complex \
"[0:a]volume=0.6[a0];[1:a]volume=1.4[a1];[a0][a1]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k "$OUT"
