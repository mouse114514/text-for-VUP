import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox, font as tkfont
import json
import os
import copy

from profile import Profile, RoleDef


ROLE_COLORS = {
    "eye": "#ff6b6b",
    "mouth": "#4ecdc4",
    "nose": "#ffe66d",
    "body": "#95e1d3",
    "hand": "#a29bfe",
}


class ConfigEditor:
    def __init__(self, profile_path=None):
        self.profile_path = profile_path
        if profile_path and os.path.exists(profile_path):
            self.profile = Profile(profile_path)
        else:
            self.profile = Profile()

        self.current_role_idx = None

        self.root = tk.Tk()
        self.root.title("VUP ASCII 角色编辑器")
        self.root.geometry("1000x700")

        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开配置...", command=self._open_profile)
        file_menu.add_command(label="保存", command=self._save_profile)
        file_menu.add_command(label="另存为...", command=self._save_as_profile)
        file_menu.add_separator()
        file_menu.add_command(label="启动 VUP", command=self._launch_vup)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menubar)

        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left = ttk.Frame(main_pane)
        right = ttk.Frame(main_pane)
        main_pane.add(left, weight=1)
        main_pane.add(right, weight=1)

        ttk.Label(left, text="ASCII 布局（直接编辑文本）", font=("", 11, "bold")).pack(anchor="w")
        self.text_editor = tk.Text(left, font=("Consolas", 18), height=15, wrap=tk.NONE)
        self.text_editor.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        self.text_editor.bind("<KeyRelease>", lambda e: self._sync_layout())

        btn_row = ttk.Frame(left)
        btn_row.pack(fill=tk.X, pady=2)
        ttk.Button(btn_row, text="从布局更新预览", command=self._sync_layout).pack(side=tk.LEFT, padx=2)

        ttk.Label(right, text="角色定义", font=("", 11, "bold")).pack(anchor="w")

        role_list_frame = ttk.Frame(right)
        role_list_frame.pack(fill=tk.X, pady=5)

        self.role_listbox = tk.Listbox(role_list_frame, height=6)
        self.role_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.role_listbox.bind("<<ListboxSelect>>", self._on_select_role)

        rl_btn = ttk.Frame(role_list_frame)
        rl_btn.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(rl_btn, text="+", width=3, command=self._add_role).pack(pady=1)
        ttk.Button(rl_btn, text="-", width=3, command=self._delete_role).pack(pady=1)

        edit_box = ttk.LabelFrame(right, text="编辑选中角色", padding=8)
        edit_box.pack(fill=tk.X, pady=5)

        row = 0
        ttk.Label(edit_box, text="名称:").grid(row=row, column=0, sticky="w")
        self.role_name_var = tk.StringVar()
        ttk.Entry(edit_box, textvariable=self.role_name_var, width=20).grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        ttk.Label(edit_box, text="类型:").grid(row=row, column=0, sticky="w")
        self.role_type_var = tk.StringVar(value="body")
        type_combo = ttk.Combobox(edit_box, textvariable=self.role_type_var,
                                   values=["eye", "mouth", "nose", "hand", "body"], state="readonly", width=12)
        type_combo.grid(row=row, column=1, sticky="w", padx=5)
        type_combo.bind("<<ComboboxSelected>>", lambda e: self._on_type_change())
        row += 1

        self.side_label = ttk.Label(edit_box, text="左右手:")
        self.side_label.grid(row=row, column=0, sticky="w")
        self.side_var = tk.StringVar(value="")
        self.side_combo = ttk.Combobox(edit_box, textvariable=self.side_var,
                                        values=["", "left", "right"], state="readonly", width=12)
        self.side_combo.grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        ttk.Label(edit_box, text="绑定到:").grid(row=row, column=0, sticky="w")
        self.bind_to_var = tk.StringVar(value="")
        self.bind_to_combo = ttk.Combobox(edit_box, textvariable=self.bind_to_var, state="readonly", width=12)
        self.bind_to_combo.grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        ttk.Label(edit_box, text="缩放倍率:").grid(row=row, column=0, sticky="w")
        self.font_scale_var = tk.StringVar(value="1.0")
        ttk.Entry(edit_box, textvariable=self.font_scale_var, width=12).grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        ttk.Label(edit_box, text="分段状态(阈值=字符):").grid(row=row, column=0, sticky="w")
        self.states_var = tk.StringVar()
        self.states_entry = ttk.Entry(edit_box, textvariable=self.states_var, width=30)
        self.states_entry.grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        ttk.Label(edit_box, text="覆盖的格子:").grid(row=row, column=0, sticky="w")
        self.cells_var = tk.StringVar()
        ttk.Entry(edit_box, textvariable=self.cells_var, width=30).grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        self.state_closed_label = ttk.Label(edit_box, text="闭合状态:")
        self.state_closed_label.grid(row=row, column=0, sticky="w")
        self.state_closed_var = tk.StringVar()
        self.state_closed_entry = ttk.Entry(edit_box, textvariable=self.state_closed_var, width=20)
        self.state_closed_entry.grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        self.state_open_label = ttk.Label(edit_box, text="张开状态:")
        self.state_open_label.grid(row=row, column=0, sticky="w")
        self.state_open_var = tk.StringVar()
        self.state_open_entry = ttk.Entry(edit_box, textvariable=self.state_open_var, width=20)
        self.state_open_entry.grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        ttk.Button(edit_box, text="应用到角色", command=self._apply_role_edit).grid(row=row, column=0, columnspan=2, pady=8)

        ttk.Label(right, text="布局预览（角色颜色标记）", font=("", 11, "bold")).pack(anchor="w", pady=(10, 0))
        self.preview_canvas = tk.Canvas(right, bg="#1a1a2e", height=250, highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, pady=5)
        self.preview_canvas.bind("<Button-1>", self._on_preview_click)

        status_row = ttk.Frame(self.root)
        status_row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(status_row, text="操作提示：编辑左侧文本 → 添加角色 → 在预览图中点击格子分配 → 设置状态字符").pack(side=tk.LEFT)

    def _sync_layout(self):
        text = self.text_editor.get("1.0", tk.END)
        lines = text.split("\n")
        self.profile.layout = [l for l in lines if not all(c == "\n" for c in l)]
        self._update_preview()

    def _refresh_all(self):
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", "\n".join(self.profile.layout))
        self._refresh_role_list()
        self._update_preview()

    def _refresh_role_list(self):
        self.role_listbox.delete(0, tk.END)
        names = []
        for r in self.profile.roles:
            tag = f" [{r.side}]" if r.side else ""
            label = f"{r.name} [{r.type}{tag}] ({len(r.cells)}格)"
            self.role_listbox.insert(tk.END, label)
            names.append(r.name)
        self.bind_to_combo["values"] = [""] + names

    def _on_select_role(self, event):
        sel = self.role_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self.current_role_idx = idx
        role = self.profile.roles[idx]
        self.role_name_var.set(role.name)
        self.role_type_var.set(role.type)
        self.side_var.set(role.side)
        self.bind_to_var.set(role.bind_to)
        self.font_scale_var.set(str(role.font_scale))
        self.cells_var.set(" ".join(f"{r},{c}" for r, c in role.cells))
        self.state_closed_var.set(role.state_closed)
        self.state_open_var.set(role.state_open)
        self.states_var.set(" ".join(f"{k}={v}" for k, v in sorted(role.states.items())))
        self._on_type_change()
        self._update_preview()

    def _on_type_change(self):
        t = self.role_type_var.get()
        has_states = t in ("eye", "mouth")
        if has_states:
            self.state_closed_label.grid()
            self.state_closed_entry.grid()
            self.state_open_label.grid()
            self.state_open_entry.grid()
        else:
            self.state_closed_label.grid_remove()
            self.state_closed_entry.grid_remove()
            self.state_open_label.grid_remove()
            self.state_open_entry.grid_remove()
        if t == "hand":
            self.side_label.grid()
            self.side_combo.grid()
        else:
            self.side_label.grid_remove()
            self.side_combo.grid_remove()

    def _apply_role_edit(self):
        if self.current_role_idx is None:
            messagebox.showinfo("提示", "请先选择一个角色")
            return
        idx = self.current_role_idx
        role = self.profile.roles[idx]
        role.name = self.role_name_var.get()
        role.type = self.role_type_var.get()
        cells_str = self.cells_var.get().strip()
        role.cells = []
        if cells_str:
            for pair in cells_str.split():
                pair = pair.strip()
                if "," in pair:
                    parts = pair.split(",")
                    if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                        role.cells.append((int(parts[0].strip()), int(parts[1].strip())))
        role.side = self.side_var.get()
        role.bind_to = self.bind_to_var.get()
        try:
            role.font_scale = float(self.font_scale_var.get())
        except ValueError:
            role.font_scale = 1.0
        if role.type in ("eye", "mouth"):
            role.state_closed = self.state_closed_var.get()
            role.state_open = self.state_open_var.get()
        raw = self.states_var.get().strip()
        role.states = {}
        if raw:
            for pair in raw.split():
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    try:
                        role.states[float(k)] = v
                    except ValueError:
                        pass
        self._refresh_role_list()
        self._update_preview()

    def _add_role(self):
        idx = len(self.profile.roles) + 1
        new_role = RoleDef(f"角色{idx}", "body", [])
        self.profile.roles.append(new_role)
        self._refresh_role_list()
        self.role_listbox.selection_clear(0, tk.END)
        self.role_listbox.selection_set(tk.END)
        self.role_listbox.event_generate("<<ListboxSelect>>")

    def _delete_role(self):
        if self.current_role_idx is None:
            return
        if messagebox.askyesno("确认", f"删除角色 '{self.profile.roles[self.current_role_idx].name}'?"):
            del self.profile.roles[self.current_role_idx]
            self.current_role_idx = None
            self._refresh_role_list()
            self._update_preview()

    def _update_preview(self):
        self.preview_canvas.delete("all")
        cw = self.preview_canvas.winfo_width() or 500
        ch = self.preview_canvas.winfo_height() or 250

        if not self.profile.layout:
            self.preview_canvas.create_text(cw // 2, ch // 2, text="(空布局)", fill="#666")
            return

        lines = self.profile.layout
        nrows = len(lines)
        ncols = max(len(l) for l in lines) if lines else 1

        cell_size = min(
            (cw - 40) // max(ncols, 1),
            (ch - 40) // max(nrows, 1),
            40,
        )
        cell_size = max(cell_size, 12)

        ox = (cw - ncols * cell_size) // 2
        oy = (ch - nrows * cell_size) // 2

        role_cell_color = {}
        for ri, role in enumerate(self.profile.roles):
            color = list(ROLE_COLORS.values())[ri % len(ROLE_COLORS)]
            for r, c in role.cells:
                role_cell_color[(r, c)] = color

        for r in range(nrows):
            for c in range(ncols):
                char = lines[r][c] if c < len(lines[r]) else " "
                x1 = ox + c * cell_size
                y1 = oy + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                bg = None
                if (r, c) in role_cell_color:
                    bg = role_cell_color[(r, c)]

                if bg:
                    self.preview_canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="", stipple="gray25")
                else:
                    self.preview_canvas.create_rectangle(x1, y1, x2, y2, fill="#2a2a3e", outline="#333")

                fs = max(8, cell_size - 8)
                self.preview_canvas.create_text(
                    (x1 + x2) // 2, (y1 + y2) // 2,
                    text=char, fill="#eee", font=("Consolas", int(fs)),
                )

                self.preview_canvas.create_text(
                    (x1 + x2) // 2, y1 + 2,
                    text=f"{r},{c}", fill="#555",
                    font=("Consolas", max(5, int(fs * 0.35))),
                    anchor="n",
                )

        self._cell_coords = []
        for r in range(nrows):
            row_coords = []
            for c in range(ncols):
                x1 = ox + c * cell_size
                y1 = oy + r * cell_size
                row_coords.append((x1, y1, x1 + cell_size, y1 + cell_size))
            self._cell_coords.append(row_coords)

    def _on_preview_click(self, event):
        if self.current_role_idx is None:
            messagebox.showinfo("提示", "请先在角色列表中选择一个角色，再点击格子分配")
            return

        if not hasattr(self, "_cell_coords") or not self._cell_coords:
            return

        for r, row in enumerate(self._cell_coords):
            for c, (x1, y1, x2, y2) in enumerate(row):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    role = self.profile.roles[self.current_role_idx]
                    if (r, c) in role.cells:
                        role.cells.remove((r, c))
                    else:
                        role.cells.append((r, c))
                    self.cells_var.set(" ".join(f"{cr},{cc}" for cr, cc in role.cells))
                    self._update_preview()
                    return

    def _sync_profile_from_ui(self):
        self._sync_layout()
        self.profile.name = "角色"

    def _open_profile(self):
        path = filedialog.askopenfilename(
            title="打开配置文件",
            filetypes=[("JSON 配置", "*.json"), ("所有文件", "*.*")],
            initialdir=os.path.dirname(self.profile_path) if self.profile_path else "profiles",
        )
        if path:
            self.profile = Profile(path)
            self.profile_path = path
            self._refresh_all()

    def _save_profile(self):
        self._sync_profile_from_ui()
        if self.profile_path:
            self.profile.save(self.profile_path)
            messagebox.showinfo("保存成功", f"已保存到 {self.profile_path}")
        else:
            self._save_as_profile()

    def _save_as_profile(self):
        self._sync_profile_from_ui()
        path = filedialog.asksaveasfilename(
            title="保存配置",
            defaultextension=".json",
            filetypes=[("JSON 配置", "*.json")],
            initialdir="profiles",
        )
        if path:
            self.profile.save(path)
            self.profile_path = path
            messagebox.showinfo("保存成功", f"已保存到 {path}")

    def _launch_vup(self):
        self._save_profile()
        if self.profile_path:
            import subprocess
            script_dir = os.path.dirname(os.path.abspath(__file__))
            subprocess.Popen(["python", "main.py", self.profile_path], cwd=script_dir)
            self.root.quit()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else None
    app = ConfigEditor(path)
    app.run()
