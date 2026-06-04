# Text for VUP

**Text for VUP** is a lightweight V‑tuber puppet tool. You define your character with multiline ASCII art, assign cells to face/eye/mouth/hand roles, and each part moves independently via webcam face and hand tracking (MediaPipe).

```
=P
oo        ← your character, driven by your face
```

## Features

- **ASCII‑art character** – write any shape with text, each cell is a pixel
- **Per‑role tracking** – eyes, mouth, nose, hands, and body each have independent offset and scale
- **Per‑role state segments** – map openness thresholds to different characters (e.g. `0=x 0.2=- 0.4==" 0.7=O`)
- **Multi‑line per role** – a role can span multiple cells across different rows
- **Left/right hands** – auto‑hide when no hand is detected
- **Bind‑to** – attach a role's movement to another (e.g. mouth follows eye)
- **Per‑role font scaling** – each role renders at its own size
- **Text outline** – black outline for readability on any background
- **Topmost & no‑focus‑steal** – hovers over other windows without stealing keyboard focus
- **Fullscreen mode** – configurable per profile
- **Built‑in profile editor** – GUI tool for layout editing, role assignment, and threshold tuning

## Quick Start

```bash
# 1. Install dependencies
pip install opencv-python mediapipe numpy pillow

# 2. Download MediaPipe models (place in models/)
#    face_landmarker_v2.task  +  hand_landmarker.task
#    from https://ai.google.dev/edge/mediapipe/solutions/vision

# 3. Run
python main.py profiles/vup.json

# Or use the profile editor
python config_editor.py profiles/vup.json
```

On Windows you can also double‑click `run.bat` or `config.bat`.

## How It Works

| File | Purpose |
|------|---------|
| `camera.py` | Webcam capture (OpenCV) |
| `tracker.py` | MediaPipe FaceLandmarker + HandLandmarker |
| `state_mapper.py` | Smoothed mapping from landmarks to openness values + region transforms |
| `profile.py` | Profile (`RoleDef`, `Profile`) – load/save JSON, resolve characters |
| `renderer.py` | Tkinter overlay window with per‑role floating text items |
| `config_editor.py` | GUI editor for profiles |
| `main.py` | Main loop: camera → tracker → mapper → renderer + debug window |

### Profile format (JSON)

```json
{
  "name": "My Character",
  "font_name": "Consolas",
  "font_size": 64,
  "layout": [ "=P", "oo" ],
  "roles": [
    {
      "name": "眼睛",
      "type": "eye",
      "cells": [[0, 0]],
      "state_closed": "x",
      "state_open": "=",
      "states": { "0": "x", "0.2": "-", "0.5": "=", "0.8": "O" },
      "font_scale": 1.5
    },
    {
      "name": "嘴巴",
      "type": "mouth",
      "cells": [[0, 1]],
      "state_closed": "P",
      "state_open": "O",
      "bind_to": "眼睛",
      "states": { "0": "P", "0.2": "p", "0.5": "o", "0.8": "0" }
    },
    {
      "name": "左手",
      "type": "hand",
      "cells": [[1, 0]],
      "side": "left"
    }
  ]
}
```

**Role types:** `eye`, `mouth`, `nose`, `hand`, `body`

**`states`** (optional) – a map of `threshold: character` pairs. The openness value picks the highest threshold ≤ current value. Falls back to `state_closed`/`state_open` if `states` is empty.

**`bind_to`** (optional) – inherit tracking offset from another role.

## License

MIT
