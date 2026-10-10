# Video workflow (approved style: v3)

For every new video, ask the user ONLY these three questions, then build:

1. **Theme** (max 3 options, chosen by the designer to fit the topic)
   - A. Cinematic Gold — dark #0a0d14, gold #f0bd4a, lens/aperture motifs (current style)
   - B. Neon Teal AI — deep navy, turquoise #47e3c3, command-bar / UI-frame motifs
   - C. Clean Editorial — warm off-white, charcoal text, gold accent, minimal
2. **Audio mode**
   - Music only (no voice file)
   - Voice file only (no music)
   - Voice + music in 2–3 sections between voice segments
   - (all modes include sound effects)
3. **Aspect ratio**: 9:16 (1080x1920) or 16:9 (1920x1080)

Pipeline: timing.py -> index.html/app.js (render(t)) -> cap.py (frames) -> audio.py (SFX/pad) -> ffmpeg mix.
Mix rule: voice loudest (loudnorm -14), SFX x0.22 lowpass 5k, music x0.2 lowpass 1.2k, both ducked by voice.

## Speech sync tool
`bash setup_asr.sh` once per container (installs sherpa-onnx + Whisper small from GitHub; HuggingFace is blocked).
Then `python3 transcribe.py voice.mp3` gives phrase text + timestamps. Dialect accuracy is approximate; verify names/brands with the user.

## Silence trimmer
`python3 trim_silence.py in.mp3 out.wav [--ratio 0.25 --min 0.12 --max 0.30]` shortens long pauses but keeps a small natural breath; out.map.json maps old->new times for rescheduling scenes.
