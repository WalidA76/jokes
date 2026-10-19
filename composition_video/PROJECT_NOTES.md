# Project notes (read first in any new session)

## Approved final video
- `out/lens_guide_with_music.mp4` — lens-choice guide, 80 s, 9:16, approved by the user.

## Saved audio assets (user-provided, Gemini-generated)
- `assets/music.mp3` — background music (first 80 s used, fade in 1.5 s / out 3.5 s).
- `assets/shutter.mp3` — iPhone camera shutter SFX, played on every photo reveal.

## Rule
- Do NOT reuse this music or shutter automatically in future videos.
  ASK the user first: "Do you want to use the same music (and shutter sound) again?"
- Font in use: Tajawal (assets/fonts). Rebuild: `python3 build_lens.py` then `python3 build_lens.py --music`.

## Video 3 — AF-ON / Back-Button Focus (76 s)
- `out/afon_back_button_focus.mp4`; code: `build_afon.py` (`python3 build_afon.py`, then `--mux`).
- Used the approved music.mp3 + shutter.mp3 (user confirmed reuse for this video).
- Photos supplied by the user: assets/afon_*.png (Canon menu, bird, runner, tripod) + lens_souk_raw.jpg (street).
- Pexels/Pixabay/Unsplash image hosts are blocked from the sandbox — B-roll must come from the user.
