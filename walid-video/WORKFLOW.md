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

## FIXED STANDARD (approved: v6) — use as the baseline for every new video
- Audio chain: trim_silence.py defaults (ratio 0.25, min 0.12s, max 0.30s) -> voice cleanup (highpass 80, afftdn, +2dB @3k, compressor 3:1, loudnorm -14).
- Mix: SFX x0.5 lowpass 9k, ducked 2.5:1 by voice; music pad x0.2 lowpass 1.2k, ducked 12:1. Voice always loudest.
- SFX set: shutter + whoosh on scene wipes, mechanical keyboard on every typing animation, bloop per bouncing dot, pop per card/chip, chime on key reveals, downward whoosh + ping on music swap.
- Timing: transcribe with the speech-sync tool (Whisper medium for final pass), set scene boundaries S[] on the trimmed voice, scenes stretch by F[i] = new/old duration.
- Timeline scene design: labeled VIDEO/VOICE/MUSIC/FX tracks, music swap gold->blue with "تغيير الموسيقى" tag, play button below.
- Intro: show the user's reference clips (Image 1 then Image 2) while they are named in the narration.
- Safe zone: text inside y 250–1480, x 70–1010 (9:16).
Git tag: v6-approved
