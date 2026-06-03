import json
import os


class RoleDef:
    def __init__(self, name, role_type, cells, state_closed="", state_open="", side=""):
        self.name = name
        self.type = role_type
        self.cells = cells
        self.state_closed = state_closed
        self.state_open = state_open
        self.side = side
        self.bind_to = ""
        self.font_scale = 1.0

    def to_dict(self):
        d = {"name": self.name, "type": self.type, "cells": self.cells, "side": self.side}
        if self.state_closed:
            d["state_closed"] = self.state_closed
        if self.state_open:
            d["state_open"] = self.state_open
        if self.bind_to:
            d["bind_to"] = self.bind_to
        if self.font_scale != 1.0:
            d["font_scale"] = self.font_scale
        return d

    @classmethod
    def from_dict(cls, d):
        raw_cells = d.get("cells", [])
        cells = [(int(r), int(c)) for r, c in raw_cells] if raw_cells else []
        obj = cls(
            d.get("name", ""), d.get("type", "body"), cells,
            d.get("state_closed", ""), d.get("state_open", ""),
            d.get("side", ""),
        )
        obj.bind_to = d.get("bind_to", "")
        obj.font_scale = d.get("font_scale", 1.0)
        return obj

    def resolve_char(self, openness):
        if self.type == "eye":
            if openness < 0.15:
                return self.state_closed or self.state_open
            elif openness > 0.7:
                return self.state_open or self.state_closed
            t = (openness - 0.15) / 0.55
            return self.state_open if t > 0.5 else self.state_closed
        elif self.type == "mouth":
            if openness < 0.15:
                return self.state_closed or self.state_open
            elif openness > 0.6:
                return self.state_open or self.state_closed
            return self.state_closed
        return ""

    def get_cell_text(self, cells_subset):
        """Return text string for a subset of this role's cells, preserving row-based gaps."""
        if not cells_subset:
            return ""
        rows = {}
        for r, c in cells_subset:
            rows.setdefault(r, []).append(c)
        sorted_rows = sorted(rows.items())
        lines = []
        for r, cols in sorted_rows:
            cols.sort()
            line_chars = []
            prev = None
            for ci, c in enumerate(cols):
                if prev is not None and c - prev > 1:
                    line_chars.append(" " * (c - prev - 1))
                line_chars.append(self._char_for_cell(r, c))
                prev = c
            lines.append("".join(line_chars))
        return "\n".join(lines)

    def _char_for_cell(self, r, c):
        idx = self.cells.index((r, c)) if (r, c) in self.cells else 0
        if idx < len(self.state_open or ""):
            return (self.state_open or "?")[idx]
        return "?"


class Profile:
    def __init__(self, path=None):
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        self.name = data.get("name", "未命名")
        self.font_name = data.get("font_name", "Consolas")
        self.font_size = data.get("font_size", 32)
        self.line_height = data.get("line_height", 1.3)
        self.window_width = data.get("window_width", 600)
        self.window_height = data.get("window_height", 400)
        self.bg_color = data.get("bg_color", [0, 0, 0])
        self.text_color = data.get("text_color", [255, 255, 255])

        self.fullscreen = data.get("fullscreen", False)
        self.x_offset = data.get("x_offset", 0)
        self.y_offset = data.get("y_offset", 0)
        self.layout = data.get("layout", ["  O   O  ", "    .    ", "   ───   "])
        self.roles = [RoleDef.from_dict(r) for r in data.get("roles", [])]

    def get_layout_width(self):
        return max(len(row) for row in self.layout) if self.layout else 0

    def get_layout_height(self):
        return len(self.layout)

    def role_at(self, row, col):
        for role in self.roles:
            if (row, col) in role.cells:
                return role
        return None

    def get_role_cells_by_row(self, role):
        """Group a role's cells by row, returning {row: [col, ...]}."""
        rows = {}
        for r, c in role.cells:
            rows.setdefault(r, []).append(c)
        return rows

    def get_grid_char(self, r, c, mapper=None):
        """Get the display character for grid position (r,c) given current states."""
        if 0 <= r < len(self.layout) and 0 <= c < len(self.layout[r]):
            base = self.layout[r][c]
            role = self.role_at(r, c)
            if role:
                val = mapper.get_part_state(role.type, role.name) if mapper else 0.5
                new_ch = role.resolve_char(val)
                if new_ch and len(new_ch) > role.cells.index((r, c)):
                    return new_ch[role.cells.index((r, c))]
            return base
        return " "

    def render_grid(self, parts_state):
        """Full grid as strings, with role state substitutions applied."""
        lines = []
        for r, row_text in enumerate(self.layout):
            chars = list(row_text)
            for c in range(len(chars)):
                role = self.role_at(r, c)
                if role:
                    val = parts_state.get(role.type, 0.5) if isinstance(parts_state, dict) else 0.5
                    new_ch = role.resolve_char(val)
                    if new_ch:
                        try:
                            idx = role.cells.index((r, c))
                            if idx < len(new_ch):
                                chars[c] = new_ch[idx]
                        except ValueError:
                            pass
            lines.append("".join(chars))
        return lines

    def get_role_by_name(self, name):
        for r in self.roles:
            if r.name == name:
                return r
        return None

    def get_role_anchor(self, role):
        """Center of a role's cells in (row, col) space."""
        if not role.cells:
            return (0, 0)
        rows = [r for r, _ in role.cells]
        cols = [c for _, c in role.cells]
        cr = (min(rows) + max(rows)) / 2.0
        cc = (min(cols) + max(cols)) / 2.0
        return (cr, cc)

    def grid_to_pixel(self, row, col):
        """Convert grid coordinates to window pixel position (center of the grid)."""
        cw = self.window_width
        ch = self.window_height
        lw = self.get_layout_width()
        lh = self.get_layout_height()
        cell_w = self.font_size * 0.6
        cell_h = self.font_size * self.line_height
        gx = cw / 2.0 + (col - lw / 2.0) * cell_w
        gy = ch / 2.0 + (row - lh / 2.0) * cell_h
        return (gx, gy)

    def to_dict(self):
        return {
            "name": self.name, "font_name": self.font_name, "font_size": self.font_size,
            "line_height": self.line_height, "window_width": self.window_width,
            "window_height": self.window_height, "fullscreen": self.fullscreen,
            "x_offset": self.x_offset, "y_offset": self.y_offset,
            "bg_color": list(self.bg_color) if isinstance(self.bg_color, tuple) else self.bg_color,
            "text_color": list(self.text_color) if isinstance(self.text_color, tuple) else self.text_color,
            "layout": self.layout, "roles": [r.to_dict() for r in self.roles],
        }

    def save(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
