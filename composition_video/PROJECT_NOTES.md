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

## Video 3 with the user's voice-over
- `assets/afon_vo.mp3` — user's recorded Arabic narration (68.6 s). Final: `out/afon_with_voiceover.mp4`.
- Scenes are time-warped to the narration (`WARP` in build_afon.py); music auto-ducks −14 dB under speech, SFX −5 dB (`python3 build_afon.py` then `--vo`).
- `out/afon_no_vo_music.mp4` = earlier version without narration.

## Inquiries intro (follower comments)
- assets/inq_post.jpg / inq_c1.jpg / inq_c2.jpg = user's post + 2 follower comments. Shown at T_out 2.0–10.2 s over the dimmed camera (see `inquiries()` in build_afon.py).
- Assumed from the user: inquiries start at s=2; comment boundaries taken from VO pauses (3.84, 6.59, 10.25). Follower comments are re-typeset (no names/avatars).

## Workshop (أساسيات التصوير) — 16:9 graphics + recording script
- Source PDF: «دليل ورشة أساسيات التصوير الفوتوغرافي». Script: workshop/workshop_recording_script.docx (+ .pdf). Content: workshop/script_content.js.
- Graphics (1920x1080, 30fps, silent): workshop/out/01..06_*.mp4 — code: workshop/build_workshop.py (`python3 build_workshop.py m1 m2 ...`).
