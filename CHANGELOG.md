# Changelog

## v0.1.0 (2026-06-04)

Initial release.

- ASCII‑art character layout with per‑cell role assignment
- Webcam face tracking via MediaPipe FaceLandmarker + HandLandmarker
- Per‑role independent offset, scale, and state (open/closed)
- Per‑role segment‑based state mapping (`states` dict)
- Left/right hand tracking with auto‑hide
- Bind‑to: inherit tracking offset from another role
- Per‑role font scaling
- Text outline effect
- Topmost window (no focus steal), fullscreen mode
- GUI profile editor (`config_editor.py`)
- Debug overlay window
