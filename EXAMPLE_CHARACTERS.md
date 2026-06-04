# 🎨 Example Characters

A collection of ASCII art character examples that you can use and customize for your own VTuber!

## 🌟 Quick-Start Characters

### Happy Face

```
  o_o
  (•)
  / \
```

**Configuration:**
- Eyes: `o_o` (closed) → `•_•` (open)
- Mouth: `(•)` (closed) → `(*)` (open)
- Body: `/ \` (static)

---

### Cute Kitten

```
  /\_/\
  (●●)
   (>>)
  /|  |\
   |  |
```

**Configuration:**
- Left eye: `●` (closed) → `○` (open)
- Right eye: `●` (closed) → `○` (open)
- Mouth: `(>>)` (closed) → `(^^)` (open)
- Ears: `/\` (static)

---

### Bunny

```
  (•  •)
    ◡
  ╱  ╲
```

**Configuration:**
- Left eye: `•` (closed) → `o` (open)
- Right eye: `•` (closed) → `o` (open)
- Mouth: `◡` (closed) → `U` (open)
- Ears: Static parts

---

## 🎭 Intermediate Characters

### Anime-Style

```
    ◇◇
   (∇)
   / \
  ∧ ∧
```

**Configuration:**
- Left eye: `◇` → `●`
- Right eye: `◇` → `●`
- Mouth: `(∇)` → `(▽)`
- Left hand: `∧` (hand role)
- Right hand: `∧` (hand role)

**Multi-state eyes:**
```json
"states": {
  0.3: "◐",
  0.6: "◑"
}
```

---

### Pixel Art Style

```
  ■■■■■
  ■◇◇■
  ■  ■
  ■■■■■
  ■  ■
  ■  ■
```

Great for retro/gaming aesthetic!

---

## 🎬 Advanced Characters

### Full Character

```
    ◇_◇
    (●)
    / \
   /∧ ∧\
  ∧    ∧
  |    |
 /     \
/       \
```

This character includes:
- Eyes: Row 0, columns 0-4
- Mouth: Row 1, column 2
- Body: Rows 2-6
- Hands: Columns 0 and 7, rows 3-5
- Legs: Rows 7-8

---

### Expressive Character

```
   ◇__◇
    ◡◡◡
    ╲▔╱
     ▏▏
    ╱ ╲
   ▏   ▏
```

Use this for comedic moments in streams!

**Multi-state mouth:**
```json
"states": {
  0.2: "□",
  0.4: "◡",
  0.6: "●",
  0.8: "▽"
}
```

---

## 🎨 Creating Your Own Character

### Step 1: Design the Layout

Start in a text editor with your ASCII art concept. Common characters:
- Eyes: `◇` `o` `●` `○` `◐` `◑`
- Mouth: `(●)` `(○)` `◡` `▽` `∧` `U` `□`
- Body: `╱` `╲` `|` `/` `\` `∧` `∨` `█`
- Decoration: `★` `☆` `♪` `♫` `❤` `✦`

### Step 2: Mark Animated Parts

Identify what needs to move:
- Eyes (follow facial expression)
- Mouth (follow facial expression)
- Hands (follow hand tracking)

### Step 3: Use the Config Editor

1. Open `python config_editor.py`
2. Paste your ASCII art in the left text box
3. Add roles with the `+` button
4. Click cells in the preview grid to assign them to roles
5. Define open/closed characters for eyes and mouth

### Step 4: Test

Click "Launch VUP" button to see your character animate in real-time!

---

## 💡 Best Practices

### Size Recommendations
- **Ideal:** 8-16 characters wide, 6-10 lines tall
- Larger = more CPU usage, smaller = poor visibility
- Test on your target resolution (1920x1080, etc.)

### Character Selection
- Use **monospace font** (Consolas, Monospace, etc.)
- Different fonts render symbols differently - test yours!
- Unicode characters may vary by OS

### Readability
- Ensure good contrast in your streaming software
- Test on actual stream thumbnail size
- Remember most viewers see it at small size

### Performance Tips
- Use 2-3 eye states max (blink + open + close)
- 2-3 mouth states for good expression
- More states = faster CPU usage
- Prefer static decorative elements over animated ones

---

## 🚀 Advanced Techniques

### Segmented States (Multi-frame Animation)

```json
{
  "name": "expressive_eye",
  "type": "eye",
  "cells": [[0, 0]],
  "state_closed": "◇",
  "state_open": "●",
  "states": {
    0.1: "◇",
    0.2: "◐",
    0.3: "◑",
    0.4: "●",
    0.5: "◑",
    0.6: "◐",
    0.7: "●",
    0.8: "◐",
    0.9: "◐",
    1.0: "●"
  }
}
```

This creates smooth eye transitions!

### Binding Positions

Attach decorative elements to body parts:

```json
{
  "name": "heart_accessory",
  "type": "body",
  "cells": [[1, 3]],
  "bind_to": "head",
  "offset": [2, 0],
  "font_scale": 1.5
}
```

This heart will move with the head!

### Left/Right Hand Independence

```json
{
  "name": "left_hand",
  "type": "hand",
  "side": "left",
  "cells": [[3, 0]],
  "font_scale": 1.2
},
{
  "name": "right_hand",
  "type": "hand",
  "side": "right",
  "cells": [[3, 6]]
}
```

---

## 📤 Share Your Creations!

Made a cool character? We'd love to see it!

**Option 1: Submit a PR**
- Add your config to `profiles/` folder
- Add description to this file
- Include ASCII preview and usage tips

**Option 2: Open an Issue**
- Paste your config JSON
- Include ASCII art preview
- Tell us about your character!

**Option 3: Start a Discussion**
- Share screenshots or GIFs
- Get feedback from community
- Collaborate on improvements

---

## 🎯 Character Ideas

Here are some fun character concepts to get inspired:

- **Animals:** Cat, dog, bunny, fox, bird, dragon
- **Robots:** Retro pixel bot, cute chibi robot, futuristic android
- **Fantasy:** Elf, dwarf, demon, angel, witch
- **Pop Culture:** Inspired by anime, games, memes
- **Abstract:** Geometric patterns, abstract expressions
- **Seasonal:** Halloween, Christmas, seasonal themes

---

**Have fun creating! 🎨✨**

For more help, see [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
