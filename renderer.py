import tkinter as tk
from tkinter import font as tkfont


class Renderer:
    def __init__(self, profile):
        self.profile = profile
        self.tc = "#FF00FF"

        self.root = tk.Tk()
        self.root.title(f"VUP - {profile.name}")
        w, h = profile.window_width, profile.window_height
        self.root.geometry(f"{w}x{h}+200+100")
        self.root.configure(bg=self.tc)
        self.root.attributes("-transparentcolor", self.tc)
        if profile.fullscreen:
            self.root.attributes("-fullscreen", True)
            w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.attributes("-topmost", True)
        self.root.update()
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010)
        except Exception:
            pass

        self.canvas = tk.Canvas(
            self.root, width=w, height=h,
            bg=self.tc, highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.base_font = tkfont.Font(family=profile.font_name or "Consolas", size=profile.font_size)
        self.text_color = self._hex(profile.text_color)
        self.outline_color = "#000000"
        self.bg_font = self.base_font
        self.role_fonts = {}

        self.bg_items = []
        self.bg_outlines = []
        self._create_text_with_outline(
            w // 2, h // 2, "", self.text_color, self.bg_font,
            "center", tk.CENTER, self.bg_items, self.bg_outlines,
        )

        self.role_items = {}
        self.role_outlines = {}
        for role in profile.roles:
            rf = tkfont.Font(family=profile.font_name or "Consolas", size=profile.font_size)
            self.role_fonts[role.name] = rf
            items, outlines = [], []
            self._create_text_with_outline(
                0, 0, "", self.text_color, rf,
                "center", tk.CENTER, items, outlines,
            )
            self.role_items[role.name] = items
            self.role_outlines[role.name] = outlines

        # Pre-measure character cell size (monospace assumed)
        self._cell_w = self.base_font.measure("A")
        self._cell_h = self.base_font.metrics("linespace") * profile.line_height

        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Escape>", lambda e: self._on_close())
        self._last_bg = ""

    def _create_text_with_outline(self, x, y, text, fill, font, anchor, justify, store, outline_store):
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in offsets:
            item = self.canvas.create_text(
                x + dx, y + dy, text=text, fill=self.outline_color,
                font=font, anchor=anchor, justify=justify,
            )
            outline_store.append(item)
        main = self.canvas.create_text(
            x, y, text=text, fill=fill,
            font=font, anchor=anchor, justify=justify,
        )
        store.append(main)

    def _hex(self, c):
        if isinstance(c, (list, tuple)):
            return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"
        return c

    def _on_close(self):
        self.running = False
        try:
            self.root.destroy()
        except Exception:
            pass

    def _px(self, row, col, role=None):
        """Grid (row,col) → window pixel, using pre-measured cell size."""
        p = self.profile
        if role and role.font_scale != 1.0:
            rf = self.role_fonts.get(role.name, self.base_font)
            cw = rf.measure("A")
            ch = rf.metrics("linespace") * p.line_height
        else:
            cw, ch = self._cell_w, self._cell_h
        gx = p.window_width / 2 + (col - p.get_layout_width() / 2) * cw + p.x_offset
        gy = p.window_height / 2 + (row - p.get_layout_height() / 2) * ch + p.y_offset
        return gx, gy

    def draw(self, profile, mapper):
        if not self.running:
            return

        # Background: role chars → spaces, same font, fixed pos
        bg_lines = []
        for r, row_text in enumerate(profile.layout):
            chars = list(row_text)
            for c in range(len(chars)):
                if profile.role_at(r, c):
                    chars[c] = " "
            bg_lines.append("".join(chars))
        bg_text = "\n".join(bg_lines)
        if bg_text != self._last_bg:
            for item in self.bg_outlines + self.bg_items:
                self.canvas.itemconfig(item, text=bg_text)
            self._last_bg = bg_text

        # Each role: floating item at anchor + per-role offset
        for role in profile.roles:
            # Hide hand roles when no hand detected
            if role.type == "hand":
                has_hand = any(h.get("side") == role.side for h in mapper.hands_data)
                if not has_hand:
                    items = self.role_items.get(role.name) or []
                    outlines = self.role_outlines.get(role.name) or []
                    for item in outlines + items:
                        self.canvas.itemconfig(item, text="")
                    continue

            # If bound to another role, inherit parent's tracking offset
            bind_src = role
            if role.bind_to:
                parent = profile.get_role_by_name(role.bind_to)
                if parent:
                    bind_src = parent
            tr = mapper.get_part_transform_for_role(bind_src)

            # Per-role font scaling (affects ONLY this role)
            new_size = max(4, int(profile.font_size * tr["scale"] * role.font_scale))
            rf = self.role_fonts.get(role.name)
            if rf:
                try:
                    rf.configure(size=new_size)
                except Exception:
                    pass

            # Build compact text (only non-empty rows)
            compact = []
            first_row = last_row = None
            for r, row_text in enumerate(profile.layout):
                seg = []
                for c in range(len(row_text)):
                    if profile.role_at(r, c) is role:
                        seg.append(profile.get_grid_char(r, c, mapper))
                    else:
                        seg.append(" ")
                line = "".join(seg).strip()
                if line:
                    compact.append(line)
                    if first_row is None:
                        first_row = r
                    last_row = r
            if not compact:
                continue

            # Anchor: center of role's actual row range, center of columns
            cols = [c for _, c in role.cells]
            ax = sum(cols) / len(cols)
            ay = (first_row + last_row) / 2.0

            bx, by = self._px(ay, ax, role)
            bx += tr["offset_x"]
            by += tr["offset_y"]
            # Shift role font size back to baseline so it matches bg alignment
            # (role font size may differ from bg, but anchor pixel uses bg metrics)

            items = self.role_items.get(role.name) or []
            outlines = self.role_outlines.get(role.name) or []
            text = "\n".join(compact)
            for i, item in enumerate(outlines + items):
                self.canvas.itemconfig(item, text=text)
                if i >= len(outlines):
                    self.canvas.coords(item, bx, by)
                else:
                    ox, oy = [(-1,-1),(-1,1),(1,-1),(1,1)][i]
                    self.canvas.coords(item, bx + ox, by + oy)

        try:
            self.root.update()
        except tk.TclError:
            self.running = False

    def is_running(self):
        return self.running

    def close(self):
        self.running = False
        try:
            self.root.destroy()
        except Exception:
            pass
