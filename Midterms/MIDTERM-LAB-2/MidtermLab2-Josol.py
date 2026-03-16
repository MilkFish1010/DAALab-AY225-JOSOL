import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv, heapq, math, time, os, random, threading

# ══════════════════════════════════════════════
#  COLOUR PALETTE
# ══════════════════════════════════════════════
C = {
    "bg":        "#06070f",
    "panel":     "#0b0d1e",
    "border":    "#1a1f3a",
    "cyan":      "#00e5ff",
    "pink":      "#ff2d78",
    "yellow":    "#ffe600",
    "green":     "#00ff9d",
    "orange":    "#ff7700",
    "purple":    "#a855f7",
    "dim":       "#2e3355",
    "text":      "#c8d0f0",
    "textdim":   "#5a6080",
    "node_bg":   "#0d1030",
    "node_src":  "#ff2d78",
    "node_dst":  "#00e5ff",
    "node_path": "#ffe600",
    "edge_dim":  "#24441e",
    "edge_path": "#ffe600",
}
# BEHOLD CYBERPUNK THEME IN ALL ITS GLORY

FONT_MONO  = ("Courier New", 10)
FONT_MONOB = ("Courier New", 10, "bold")
FONT_TITLE = ("Courier New", 14, "bold")
FONT_SMALL = ("Courier New", 8)

def blend_with_bg(hex_color, alpha):
    def _hex_to_rgb(h):
        return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
    try:
        fg = _hex_to_rgb(hex_color)
    except Exception:
        fg = (0, 0, 0)
    bg = _hex_to_rgb(C["bg"])
    r = round(fg[0]*alpha + bg[0]*(1-alpha))
    g = round(fg[1]*alpha + bg[1]*(1-alpha))
    b = round(fg[2]*alpha + bg[2]*(1-alpha))
    return f"#{r:02x}{g:02x}{b:02x}"

def contrast_color(hex_color):
    """Return black or dark bg if the color is bright, white/light if dark."""
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        luminance = 0.299*r + 0.587*g + 0.114*b
        if luminance > 140:
            return "#000000"  # dark bg
        else:
            return "#ffffff"
    except Exception:
        return "#ffffff"

# Global mapping assigned after CSV load: (U,V) -> hex color
EDGE_COLOR_MAP = {}

# explicit overrides requested by user (directed edges)
# Leave empty for fully dynamic coloring across all datasets
EDGE_OVERRIDES = {}

def hsl_to_hex(h, s, l):
    c = (1 - abs(2*l - 1)) * s
    hp = h / 60.0
    x = c * (1 - abs(hp % 2 - 1))
    if 0 <= hp < 1:
        r1, g1, b1 = c, x, 0
    elif 1 <= hp < 2:
        r1, g1, b1 = x, c, 0
    elif 2 <= hp < 3:
        r1, g1, b1 = 0, c, x
    elif 3 <= hp < 4:
        r1, g1, b1 = 0, x, c
    elif 4 <= hp < 5:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x
    m = l - c/2
    r = int(round((r1 + m) * 255))
    g = int(round((g1 + m) * 255))
    b = int(round((b1 + m) * 255))
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_distinct_colors(n):
    colors = []
    gr = 0.618033988749895
    for i in range(n):
        frac = (i * gr) % 1.0
        hue = frac * 360.0
        sat = 0.6 + (0.3 * ((i % 3) / 2.0))
        light = 0.35 + (0.25 * (((i//3) % 3) / 2.0))
        colors.append(hsl_to_hex(hue, sat, light))
    return colors

def assign_edge_colors(edges):
    global EDGE_COLOR_MAP
    EDGE_COLOR_MAP = {}
    pairs = []
    seen = set()
    for e in edges:
        u, v = e[0].upper(), e[1].upper()
        if (u, v) in seen: continue
        seen.add((u, v))
        pairs.append((u, v))

    remaining = []
    for p in pairs:
        if p in EDGE_OVERRIDES:
            EDGE_COLOR_MAP[p] = EDGE_OVERRIDES[p]
        else:
            remaining.append(p)

    pal = generate_distinct_colors(len(remaining)) if remaining else []
    for p, col in zip(remaining, pal):
        EDGE_COLOR_MAP[p] = col

def pick_edge_color(u, v):
    key = (u.upper(), v.upper())
    if key in EDGE_COLOR_MAP:
        return EDGE_COLOR_MAP[key]
    if key in EDGE_OVERRIDES:
        return EDGE_OVERRIDES[key]
    hval = 0
    s = f"{u}|{v}"
    for ch in s:
        hval = (hval * 1315423911 + ord(ch)) & 0xFFFFFFFF
    frac = (hval * 0.618033988749895) % 1.0
    hue = frac * 360.0
    sat = 0.7
    light = 0.45
    return hsl_to_hex(hue, sat, light)

# ══════════════════════════════════════════════
#  NODE POSITIONS  (normalised 0-1)
# ══════════════════════════════════════════════
BASE_POS = {
    "DASMA":    (0.15, 0.15),
    "BACOOR":   (0.5, 0.15),
    "IMUS":     (0.85, 0.15),
    "SILANG":   (0.5, 0.5),
    "NOVELETA": (0.85, 0.5),
    "KAWIT":    (0.15, 0.85),
    "INDANG":   (0.5, 0.85),
    "GENTRI":   (0.85, 0.85),
}

# ══════════════════════════════════════════════
#  DIJKSTRA
# ══════════════════════════════════════════════
def dijkstra(graph, source, target, weight_key):
    dist  = {n: float('inf') for n in graph}
    prev  = {n: None for n in graph}
    steps = []
    dist[source] = 0
    pq = [(0, source)]
    visited = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        steps.append({"visit": u, "dist_so_far": d,
                       "dist_table": dict(dist), "prev_table": dict(prev)})
        if u == target:
            break
        for v, attrs in graph.get(u, {}).items():
            w  = attrs[weight_key]
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                steps.append({"relax": (u, v), "new_dist": nd,
                               "dist_table": dict(dist), "prev_table": dict(prev)})
                heapq.heappush(pq, (nd, v))
    path, cur = [], target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    if not path or path[0] != source:
        return [], float('inf'), []
    return path, dist[target], steps

def path_totals(graph, path):
    td = tt = tf = 0.0
    for i in range(len(path)-1):
        e = graph[path[i]][path[i+1]]
        td += e['distance']; tt += e['time']; tf += e['fuel']
    return td, tt, tf

# ══════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAVITE GRID — Travelling Salesman PATHFINDER v2.77")
        self.configure(bg=C["bg"])
        self.minsize(1200, 720)
        # Start fullscreen by default
        if os.name == 'nt':
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)
        self.after(100, self._ensure_fullscreen)

        self.graph   = {}
        self.edges   = []
        self.nodes   = []
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        default_csv = os.path.join(self.base_dir, "dataset.csv")
        self.csv_path = tk.StringVar(value=default_csv)

        self.src_var = tk.StringVar(value="IMUS")
        self.dst_var = tk.StringVar(value="GENTRI")
        self.map_metric_var = tk.StringVar(value="distance")
        self.bidir_var = tk.BooleanVar(value=False)  # Bidirectional toggle

        self.result_dist = {}
        self.result_time = {}
        self.result_fuel = {}

        self._anim_particles = []
        self._pulse_phase = 0.0
        self._anim_job = None
        self._path_anim_progress = {}
        self._jet_progress = 0.0
        self._animation_running = False
        self._computing = False
        self._bidir_blink_phase = 0.0  # For blinking bidirectional button

        # Node drag state
        self._drag_node = None
        self._node_positions = dict(BASE_POS)  # mutable copy

        self._build_ui()
        self._start_bg_anim()

        if os.path.exists(default_csv):
            self.csv_path.set(default_csv)
            self._load_csv(default_csv)

    # ─────────────────────────────────────────
    #  UI BUILD
    # ─────────────────────────────────────────
    def _build_ui(self):
        top = tk.Frame(self, bg=C["bg"], pady=6)
        top.pack(fill="x", padx=12, pady=(8,0))

        tk.Label(top, text="◈ CAVITE NEURAL GRID ◈",
                 bg=C["bg"], fg=C["cyan"],
                 font=("Courier New", 18, "bold")).pack(side="left")

        tk.Label(top, text="PATHFINDING MODULE // DIJKSTRA PROTOCOL",
                 bg=C["bg"], fg=C["textdim"],
                 font=("Courier New", 9)).pack(side="left", padx=18)

        right = tk.Frame(top, bg=C["bg"])
        right.pack(side="right")
        tk.Label(right, text="CSV:", bg=C["bg"], fg=C["textdim"],
                 font=FONT_MONO).pack(side="left")
        tk.Entry(right, textvariable=self.csv_path, width=26,
                 bg=C["panel"], fg=C["cyan"], insertbackground=C["cyan"],
                 relief="flat", font=FONT_MONO,
                 highlightthickness=1, highlightbackground=C["border"],
                 highlightcolor=C["cyan"]).pack(side="left", padx=4)
        self._btn(right, "BROWSE", self._browse).pack(side="left", padx=2)
        self._btn(right, "LOAD",   self._load).pack(side="left", padx=2)

        # ── Control bar ──────────────────────
        ctrl = tk.Frame(self, bg=C["panel"],
                        highlightthickness=1, highlightbackground=C["border"])
        ctrl.pack(fill="x", padx=12, pady=6)

        tk.Label(ctrl, text=" SOURCE:", bg=C["panel"], fg=C["pink"],
                 font=FONT_MONOB).pack(side="left", padx=(12,2))
        self.src_cb = ttk.Combobox(ctrl, textvariable=self.src_var,
                                   width=12, font=FONT_MONO, state="readonly")
        self._style_combo(self.src_cb)
        self.src_cb.pack(side="left", padx=4)

        tk.Label(ctrl, text="TARGET:", bg=C["panel"], fg=C["cyan"],
                 font=FONT_MONOB).pack(side="left", padx=(18,2))
        self.dst_cb = ttk.Combobox(ctrl, textvariable=self.dst_var,
                                   width=12, font=FONT_MONO, state="readonly")
        self._style_combo(self.dst_cb)
        self.dst_cb.pack(side="left", padx=4)

        # Bidirectional toggle
        self.bidir_btn = tk.Checkbutton(ctrl, text="↔ ALL BIDIRECTIONAL MODE",
                                        variable=self.bidir_var,
                                        command=self._on_bidir_toggle_safe,
                                        bg=C["panel"], fg=C["purple"],
                                        activebackground=C["panel"],
                                        activeforeground=C["purple"],
                                        selectcolor=C["border"],
                                        font=FONT_MONOB,
                                        relief="flat", bd=0,
                                        highlightthickness=1,
                                        highlightbackground=C["border"],
                                        highlightcolor=C["purple"],
                                        padx=8, pady=4)
        self.bidir_btn.pack(side="left", padx=8)

        self._btn(ctrl, "▶  FIND PATHS", self._run, fg=C["yellow"],
                  bg="#1a1500").pack(side="left", padx=14)

        self.status_lbl = tk.Label(ctrl, text="◌ AWAITING DATA",
                                   bg=C["panel"], fg=C["textdim"],
                                   font=FONT_MONO)
        self.status_lbl.pack(side="left", padx=14)

        # ── Notebook ─────────────────────────
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Cyber.TNotebook",
                        background=C["bg"], borderwidth=0)
        style.configure("Cyber.TNotebook.Tab",
                        background=C["panel"], foreground=C["textdim"],
                        font=("Courier New", 10, "bold"),
                        padding=[16,6], borderwidth=0)
        style.map("Cyber.TNotebook.Tab",
                  background=[("selected", C["border"])],
                  foreground=[("selected", C["cyan"])])

        nb = ttk.Notebook(self, style="Cyber.TNotebook")
        nb.pack(fill="both", expand=True, padx=12, pady=(0,8))

        self.tab_map  = tk.Frame(nb, bg=C["bg"])
        nb.add(self.tab_map, text="  ◈ NODE MAP  ")
        self._build_map_tab()

        self.tab_dbg  = tk.Frame(nb, bg=C["bg"])
        nb.add(self.tab_dbg, text="  ⬡ DEBUG / STEPS  ")
        self._build_debug_tab()

        self.nb = nb

    # ─────────────────────────────────────────
    #  TAB 1: NODE MAP CANVAS
    # ─────────────────────────────────────────
    def _build_map_tab(self):
        top_f = tk.Frame(self.tab_map, bg=C["bg"])
        top_f.pack(fill="x", padx=16, pady=8)
        tk.Label(top_f, text="DISPLAY PATH:", bg=C["bg"], fg=C["textdim"],
                 font=FONT_MONOB).pack(side="left", padx=(0, 12))
        for text, val, col in [("DISTANCE", "distance", C["cyan"]),
                                ("TIME", "time", C["green"]),
                                ("FUEL", "fuel", C["orange"])]:
            rb = tk.Radiobutton(top_f, text=text, variable=self.map_metric_var,
                                value=val, command=self._redraw_map,
                                bg=C["bg"], fg=col, selectcolor=C["panel"],
                                activebackground=C["bg"], activeforeground=col,
                                font=FONT_MONOB, indicatoron=False,
                                relief="flat", bd=0,
                                highlightthickness=1,
                                highlightbackground=C["border"],
                                highlightcolor=col,
                                padx=10, pady=4)
            rb.pack(side="left", padx=4)

        tk.Label(top_f, text="  ⟳ DRAG NODES TO REPOSITION",
                 bg=C["bg"], fg=C["textdim"],
                 font=("Courier New", 8)).pack(side="left", padx=18)

        # Canvas with map results drawn as overlays
        content = tk.Frame(self.tab_map, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=12, pady=(0,8))
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(content, bg=C["bg"],
                                highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self._redraw_map())

        # Tooltip
        self._tooltip_win = None
        self._tooltip_node = None
        self.canvas.bind("<Motion>",        self._on_canvas_motion)
        self.canvas.bind("<Leave>",         self._hide_tooltip)

        # Drag bindings
        self.canvas.bind("<ButtonPress-1>",   self._on_drag_start)
        self.canvas.bind("<B1-Motion>",       self._on_drag_move)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)

    # ─────────────────────────────────────────
    #  NODE DRAG
    # ─────────────────────────────────────────
    def _on_drag_start(self, event):
        hit = self._hit_node(event.x, event.y)
        if hit:
            self._drag_node = hit
            self._hide_tooltip()

    def _on_drag_move(self, event):
        if not self._drag_node:
            return
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W < 10 or H < 10:
            return
        mx = 0.10; my = 0.12
        # Invert _sc: nx_ = (x/W - mx) / (1 - 2*mx)
        nx_ = (event.x / W - mx) / (1 - 2*mx)
        ny_ = (event.y / H - my) / (1 - 2*my)
        nx_ = max(0.01, min(0.99, nx_))
        ny_ = max(0.01, min(0.99, ny_))
        self._node_positions[self._drag_node] = (nx_, ny_)
        self._redraw_map()

    def _on_drag_end(self, event):
        self._drag_node = None

    def _hit_node(self, ex, ey):
        if not hasattr(self, '_node_hit_areas'):
            return None
        for node, (x, y) in self._node_hit_areas.items():
            if abs(ex - x) < 50 and abs(ey - y) < 50:
                return node
        return None



    # ─────────────────────────────────────────
    #  FULLSCREEN FALLBACK
    # ─────────────────────────────────────────
    def _ensure_fullscreen(self):
        """Ensure window is fullscreen after initialization."""
        try:
            if os.name == 'nt':
                self.state('zoomed')
            else:
                self.attributes('-zoomed', True)
        except:
            pass

    # ─────────────────────────────────────────
    #  TAB 2: DEBUG
    # ─────────────────────────────────────────
    def _build_debug_tab(self):
        top = tk.Frame(self.tab_dbg, bg=C["bg"])
        top.pack(fill="x", padx=16, pady=(12,4))
        tk.Label(top, text="DIJKSTRA STEP-BY-STEP VERIFICATION",
                 bg=C["bg"], fg=C["purple"],
                 font=FONT_TITLE).pack(side="left")

        self.dbg_metric = tk.StringVar(value="distance")
        for text, val, col in [("DISTANCE", "distance", C["cyan"]),
                                ("TIME",     "time",     C["green"]),
                                ("FUEL",     "fuel",     C["orange"])]:
            rb = tk.Radiobutton(top, text=text, variable=self.dbg_metric,
                                value=val, command=self._refresh_debug,
                                bg=C["bg"], fg=col, selectcolor=C["panel"],
                                activebackground=C["bg"], activeforeground=col,
                                font=FONT_MONOB, indicatoron=False,
                                relief="flat", bd=0,
                                highlightthickness=1,
                                highlightbackground=C["border"],
                                highlightcolor=col,
                                padx=10, pady=4)
            rb.pack(side="left", padx=6)

        pw = tk.PanedWindow(self.tab_dbg, orient="horizontal",
                            bg=C["border"], sashwidth=4,
                            sashrelief="flat")
        pw.pack(fill="both", expand=True, padx=12, pady=8)

        # Left: step list
        left_f = tk.Frame(pw, bg=C["bg"])
        pw.add(left_f, minsize=340)

        tk.Label(left_f, text=" ALGORITHM STEPS",
                 bg=C["panel"], fg=C["purple"],
                 font=FONT_MONOB, anchor="w").pack(fill="x")

        self.steps_listbox = tk.Listbox(
            left_f, bg=C["bg"], fg=C["text"],
            font=("Courier New", 9),
            selectbackground=C["border"],
            selectforeground=C["text"],   # ← no yellow fg on selection
            highlightthickness=1, highlightbackground=C["border"],
            activestyle="none", relief="flat",
            exportselection=False)
        self.steps_listbox.pack(fill="both", expand=True, side="left")
        sb = tk.Scrollbar(left_f, command=self.steps_listbox.yview,
                          bg=C["panel"], troughcolor=C["bg"],
                          highlightthickness=0, relief="flat")
        sb.pack(side="right", fill="y")
        self.steps_listbox.config(yscrollcommand=sb.set)
        self.steps_listbox.bind("<<ListboxSelect>>", self._on_step_select)

        # Right: dist table + arithmetic panel
        right_f = tk.Frame(pw, bg=C["bg"])
        pw.add(right_f, minsize=400)

        tk.Label(right_f, text=" DISTANCE TABLE AT SELECTED STEP",
                 bg=C["panel"], fg=C["purple"],
                 font=FONT_MONOB, anchor="w").pack(fill="x")

        cols = ("NODE","DIST","PREV","STATUS")
        style = ttk.Style()
        style.configure("Debug.Treeview",
                        background=C["bg"], foreground=C["text"],
                        fieldbackground=C["bg"],
                        font=("Courier New", 9),
                        rowheight=22)
        style.configure("Debug.Treeview.Heading",
                        background=C["panel"], foreground=C["purple"],
                        font=("Courier New", 9, "bold"))
        style.map("Debug.Treeview",
                  background=[("selected", C["border"])],
                  foreground=[("selected", C["text"])])

        self.dbg_tree = ttk.Treeview(right_f, columns=cols,
                                     show="headings",
                                     style="Debug.Treeview")
        for col in cols:
            self.dbg_tree.heading(col, text=col)
            self.dbg_tree.column(col, width=90, anchor="center")
        self.dbg_tree.pack(fill="both", expand=True)

        # ── Arithmetic computation panel ──────
        arith_frame = tk.Frame(right_f, bg=C["panel"],
                               highlightthickness=1,
                               highlightbackground=C["purple"])
        arith_frame.pack(fill="x", padx=0, pady=(4,0))

        tk.Label(arith_frame, text="  ⬡ EDGE ARITHMETIC — RELAXATION DETAIL",
                 bg=C["panel"], fg=C["purple"],
                 font=("Courier New", 9, "bold"),
                 anchor="w").pack(fill="x")

        self.arith_text = tk.Text(arith_frame, bg=C["bg"], fg=C["text"],
                                  font=("Courier New", 9),
                                  height=6, state="disabled",
                                  relief="flat",
                                  highlightthickness=0)
        self.arith_text.pack(fill="x", padx=6, pady=(2,6))

        # Summary box
        self.dbg_summary = tk.Text(self.tab_dbg, bg=C["panel"],
                                   fg=C["text"], font=("Courier New",9),
                                   height=5, state="disabled",
                                   relief="flat",
                                   highlightthickness=1,
                                   highlightbackground=C["border"])
        self.dbg_summary.pack(fill="x", padx=12, pady=(0,8))

    # ─────────────────────────────────────────
    #  WIDGET HELPERS
    # ─────────────────────────────────────────
    def _btn(self, parent, text, cmd, fg=C["cyan"], bg=C["panel"]):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg=fg, activebackground=C["border"],
                      activeforeground=fg,
                      font=("Courier New", 9, "bold"),
                      relief="flat", padx=10, pady=4,
                      cursor="hand2",
                      highlightthickness=1,
                      highlightbackground=fg,
                      highlightcolor=fg)
        return b

    def _style_combo(self, cb):
        s = ttk.Style()
        s.configure("Cyber.TCombobox",
                    fieldbackground=C["panel"],
                    background=C["panel"],
                    foreground=C["cyan"],
                    selectbackground=C["border"],
                    selectforeground=C["cyan"])
        cb.configure(style="Cyber.TCombobox")

    # ─────────────────────────────────────────
    #  CSV LOAD
    # ─────────────────────────────────────────
    def _browse(self):
        f = filedialog.askopenfilename(filetypes=[("CSV","*.csv"),("All","*.*")])
        if f:
            self.csv_path.set(f)

    def _load(self):
        p = self.csv_path.get().strip()
        p = os.path.expanduser(p)
        if not os.path.isabs(p):
            p = os.path.join(self.base_dir, p)
        p = os.path.normpath(p)
        self.csv_path.set(p)
        self._load_csv(p)

    def _on_bidir_toggle_safe(self):
        """Reload CSV when bidirectional toggle is changed (with protection)."""
        if self._computing:
            self.bidir_var.set(not self.bidir_var.get())
            return
        p = self.csv_path.get().strip()
        p = os.path.expanduser(p)
        if not os.path.isabs(p):
            p = os.path.join(self.base_dir, p)
        p = os.path.normpath(p)
        if os.path.exists(p):
            self._load_csv(p)

    def _load_csv(self, path):
        try:
            graph = {}
            edges = []
            nodes_set = set()
            print(f"[DEBUG] Attempting to load CSV at: {path}")
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    u = row['from_node'].strip().upper()
                    v = row['to_node'].strip().upper()
                    d = float(row['distance'])
                    t = float(row['time'])
                    fl= float(row['fuel'])
                    if u not in graph: graph[u] = {}
                    graph[u][v] = {'distance':d,'time':t,'fuel':fl}
                    edges.append((u,v,d,t,fl))
                    nodes_set.add(u); nodes_set.add(v)
            
            # Add bidirectional edges if toggle is enabled
            if self.bidir_var.get():
                reverse_edges = []
                for u, v, d, t, fl in edges:
                    if v not in graph: graph[v] = {}
                    # Only add reverse if it doesn't already exist
                    if u not in graph[v]:
                        graph[v][u] = {'distance':d,'time':t,'fuel':fl}
                        reverse_edges.append((v, u, d, t, fl))
                edges.extend(reverse_edges)
                print(f"[DEBUG] Bidirectional mode: Added {len(reverse_edges)} reverse edges")
            
            self.graph = graph
            self.edges = edges
            self.nodes = sorted(nodes_set)
            # Reset node positions to base
            self._node_positions = dict(BASE_POS)
            try:
                assign_edge_colors(self.edges)
            except Exception:
                pass
            print(f"[DEBUG] Loaded edges={len(edges)} nodes={len(self.nodes)}")
            print(f"[DEBUG] Graph structure:")
            for node in sorted(self.graph.keys()):
                neighbors = ", ".join([f"{v}({self.graph[node][v]['time']}min)" for v in sorted(self.graph[node].keys())])
                print(f"  {node} → {neighbors}")

            for cb in [self.src_cb, self.dst_cb]:
                cb['values'] = self.nodes
            if "IMUS"   in self.nodes: self.src_var.set("IMUS")
            if "GENTRI" in self.nodes: self.dst_var.set("GENTRI")

            self._set_status(f"✔ LOADED {len(edges)} EDGES, {len(self.nodes)} NODES", C["green"])
            self._run()
        except Exception as ex:
            messagebox.showerror("Load Error", str(ex))
            self._set_status(f"✘ LOAD FAILED: {ex}", C["pink"])

    # ─────────────────────────────────────────
    #  RUN DIJKSTRA  (with same-node check)
    # ─────────────────────────────────────────
    def _run(self):
        if self._computing:
            return
        
        if not self.graph:
            self._set_status("✘ NO DATA LOADED", C["pink"]); return
        src = self.src_var.get(); dst = self.dst_var.get()
        if not src or not dst:
            self._set_status("✘ SELECT SOURCE AND TARGET", C["pink"]); return
        if src == dst:
            messagebox.showerror(
                "Invalid Selection",
                f"Source and Target cannot be the same node.\n\nSelected: {src}"
            )
            self._set_status("✘ SOURCE AND TARGET ARE THE SAME NODE", C["pink"])
            return

        self._computing = True
        self._disable_inputs()
        self._set_status("⟳ COMPUTING...", C["yellow"])
        self.update_idletasks()

        results = {}
        for metric in ['distance','time','fuel']:
            path, total, steps = dijkstra(self.graph, src, dst, metric)
            td, tt, tf = path_totals(self.graph, path) if path else (0,0,0)
            results[metric] = {"path":path,"total":total,"steps":steps,
                               "td":td,"tt":tt,"tf":tf}
            print(f"[DEBUG] {metric.upper()}: {src} → {dst}")
            print(f"  Path: {' → '.join(path) if path else 'NO PATH'}")
            print(f"  Total: {total} | Calculated: {[td, tt, tf]}")
        self.results = results
        self._path_anim_progress = {k:0.0 for k in results}
        self._computing = False
        self._enable_inputs()

        self._set_status(
            f"✔ {src} ──► {dst}   DIST:{results['distance']['td']}km  "
            f"TIME:{results['time']['tt']}min  FUEL:{results['fuel']['tf']:.1f}L",
            C["green"])

        self._redraw_map()
        self._animate_paths()
        self._refresh_debug()

    # ─────────────────────────────────────────
    #  RESULTS TAB UPDATE
    # ─────────────────────────────────────────
    # ─────────────────────────────────────────
    #  MAIN NODE MAP
    # ─────────────────────────────────────────
    def _redraw_map(self):
        c = self.canvas
        c.delete("all")
        W = c.winfo_width(); H = c.winfo_height()
        if W < 10 or H < 10: return

        self._draw_map_bg(c, W, H)
        self._draw_map_edges(c, W, H)
        self._draw_map_nodes(c, W, H)
        self._draw_map_jets(c, W, H)
        self._draw_map_legend(c, W, H)
        self._draw_map_results(c, W, H)

    def _draw_map_bg(self, c, W, H):
        c.create_rectangle(0,0,W,H, fill=C["bg"], outline="")
        for gx in range(0, W, max(1,W//20)):
            c.create_line(gx,0,gx,H, fill=C["border"], width=1)
        for gy in range(0, H, max(1,H//15)):
            c.create_line(0,gy,W,gy, fill=C["border"], width=1)
        for bx,by,cx_,cy_ in [(10,10,60,10),(10,10,10,60),
                               (W-10,10,W-60,10),(W-10,10,W-10,60),
                               (10,H-10,60,H-10),(10,H-10,10,H-60),
                               (W-10,H-10,W-60,H-10),(W-10,H-10,W-10,H-60)]:
            c.create_line(bx,by,cx_,cy_, fill=C["cyan"], width=2)

        c.create_text(W//2, 22, text="◈  CAVITE NODE MAP  ◈",
                      fill=C["cyan"], font=("Courier New",20,"bold"))
        c.create_text(W//2, 42, text="// DIRECTED GRAPH — ALL CONNECTIONS //",
                      fill=C["textdim"], font=("Courier New",12))

    def _sc(self, nx_, ny_, W, H):
        mx = 0.10; my = 0.12
        return (mx + nx_*(1-2*mx))*W, (my + ny_*(1-2*my))*H

    def _is_bidirectional_edge(self, u, v):
        """Check if edge (u,v) has a reverse edge (v,u) with same attributes."""
        if u not in self.graph or v not in self.graph[u]:
            return False
        if v not in self.graph or u not in self.graph[v]:
            return False
        # Check if both directions exist with same attributes
        attrs_uv = self.graph[u][v]
        attrs_vu = self.graph[v][u]
        return (attrs_uv['distance'] == attrs_vu['distance'] and
                attrs_uv['time'] == attrs_vu['time'] and
                attrs_uv['fuel'] == attrs_vu['fuel'])

    def _draw_map_edges(self, c, W, H):
        if not hasattr(self,'results'): results = {}
        else: results = self.results

        path_edges = {}
        metric = self.map_metric_var.get()
        metric_colors = {'distance':C["cyan"],'time':C["green"],'fuel':C["orange"]}
        if metric in results:
            color = metric_colors[metric]
            path = results.get(metric,{}).get('path',[])
            for i in range(len(path)-1):
                path_edges[(path[i],path[i+1])] = color

        # Track which edges we've already drawn to skip reverse pairs
        drawn_edges = set()

        for u,v,d,t,f in self.edges:
            pos = self._node_positions
            if u not in pos or v not in pos: continue
            
            # Skip if reverse of this edge was already drawn
            if (v, u) in drawn_edges:
                continue
            
            x1,y1 = self._sc(*pos[u],W,H)
            x2,y2 = self._sc(*pos[v],W,H)

            # Check if edge is in path (either direction for bidirectional)
            is_path = (u,v) in path_edges or (v,u) in path_edges
            col = path_edges.get((u,v)) if (u,v) in path_edges else (path_edges.get((v,u)) if (v,u) in path_edges else pick_edge_color(u, v))
            is_bidir = self._is_bidirectional_edge(u, v)
            lw  = 6 if is_path else 1
            alpha_tag = "path_edge" if is_path else "dim_edge"

            # Calculate both endpoints pulled back from nodes
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist > 0:
                back_dist_start = 35
                back_dist_end = 45
                norm_x, norm_y = dx / dist, dy / dist
                start_x, start_y = x1 + norm_x * back_dist_start, y1 + norm_y * back_dist_start
                end_x, end_y = x2 - norm_x * back_dist_end, y2 - norm_y * back_dist_end
            else:
                start_x, start_y = x1, y1
                end_x, end_y = x2, y2

            if is_path:
                # Draw glow layers first (without arrows)
                for glw, gcol in [
                    (18, blend_with_bg(col, 0.5)),
                    (12, blend_with_bg(col, 0.7)),
                ]:
                    c.create_line(start_x,start_y,end_x,end_y, fill=gcol, width=glw,
                                  tags=alpha_tag)
                # Draw top layer with visible arrows
                arrow_type = "both" if is_bidir else "last"
                arrow_shape = (25, 35, 12)
                c.create_line(start_x,start_y,end_x,end_y, fill=col, width=lw,
                              arrow=arrow_type, arrowshape=arrow_shape,
                              tags=alpha_tag)
            else:
                arrow_type = "both" if is_bidir else "last"
                arrow_shape = (20, 28, 10)
                c.create_line(start_x,start_y,end_x,end_y, fill=col, width=lw,
                              arrow=arrow_type, arrowshape=arrow_shape,
                              dash=(4,6))

            # Edge label — bigger font, contrasted on path
            mx_ = (x1+x2)/2; my_ = (y1+y2)/2
            seg_len = math.hypot(x2-x1, y2-y1) + 1e-9
            off_x = -(y2-y1)/seg_len * 18
            off_y =  (x2-x1)/seg_len * 18
            if is_path:
                # Use white for highlighted edge labels
                lbl_col = "#ffffff"
                c.create_text(mx_+off_x, my_+off_y,
                              text=f"{d:.0f}km / {t:.0f}min / {f}L",
                              fill=lbl_col,
                              font=("Courier New", 13, "bold"),
                              tags="edge_label")
            else:
                c.create_text(mx_+off_x, my_+off_y,
                              text=f"{d:.0f}km / {t:.0f}min / {f}L",
                              fill=col,
                              font=("Courier New", 13),
                              tags="edge_label")
            
            # Mark this edge as drawn
            drawn_edges.add((u, v))


    def _draw_map_nodes(self, c, W, H):
        if not hasattr(self,'results'): results = {}
        else: results = self.results

        path_nodes = {}
        metric = self.map_metric_var.get()
        metric_colors = {'distance':C["cyan"],'time':C["green"],'fuel':C["orange"]}
        if metric in results:
            color = metric_colors[metric]
            path = results.get(metric,{}).get('path',[])
            for node in path:
                path_nodes.setdefault(node,[]).append(color)

        src = self.src_var.get(); dst = self.dst_var.get()

        for node, (nx_, ny_) in self._node_positions.items():
            if node not in self.nodes: continue
            x, y = self._sc(nx_, ny_, W, H)
            colors = path_nodes.get(node,[])

            r = 41
            if node == src:
                nc = C["node_src"]; ring = C["pink"]
            elif node == dst:
                nc = C["node_dst"]; ring = C["cyan"]
            elif colors:
                nc = C["node_path"]; ring = colors[0]
            else:
                nc = C["node_bg"]; ring = C["dim"]

            if colors or node in (src,dst):
                for gr in [r+22, r+16, r+10, r+4]:
                    c.create_oval(x-gr,y-gr,x+gr,y+gr,
                                  fill="", outline=blend_with_bg(ring, 0.25), width=1)

            if len(colors)>1:
                for i,col in enumerate(colors[:3]):
                    start = i*120; extent=118
                    c.create_arc(x-r-3,y-r-3,x+r+3,y+r+3,
                                 start=start,extent=extent,
                                 outline=col, width=2, style="arc")

            c.create_oval(x-r,y-r,x+r,y+r,
                          fill=nc, outline=ring, width=3 if colors else 2,
                          tags=f"node_{node}")

            # Node label: inverted to ring color for highlighted nodes
            if node in (src, dst) or colors:
                txt_fg = contrast_color(nc)
            else:
                txt_fg = C["text"]

            c.create_text(x, y, text=node,
                          fill=txt_fg,
                          font=("Courier New", 13, "bold"),
                          tags=f"node_{node}")

            out_deg = len(self.graph.get(node,{}))
            c.create_text(x, y+r+12,
                          text=f"[{out_deg}→]",
                          fill=ring, font=("Courier New", 12))

        self._node_hit_areas = {
            node: self._sc(*pos, W, H)
            for node, pos in self._node_positions.items()
            if node in self.nodes
        }

    def _draw_map_jets(self, c, W, H):
        """Draw animated jet symbols flying along the shortest path."""
        if not hasattr(self, 'results'):
            return
        
        results = self.results
        if not results:
            return
        
        # Get the currently displayed metric path
        metric = self.map_metric_var.get()
        path = results.get(metric, {}).get('path', [])
        
        # Only draw jet if there's a valid path
        if not path or len(path) < 2:
            return
        
        # Get animation progress (0.0 to 1.0, loops infinitely)
        if not hasattr(self, '_jet_progress'):
            self._jet_progress = 0.0
        
        progress = self._jet_progress
        
        # Calculate which edge the jet is on and its position within that edge
        path_length = len(path) - 1
        jet_position = progress * path_length
        edge_idx = int(jet_position)
        edge_progress = jet_position - edge_idx
        
        # Clamp to valid edge (in case of floating point errors)
        if edge_idx >= path_length:
            edge_idx = path_length - 1
            edge_progress = 1.0
        
        # Get the two nodes for the current edge
        u = path[edge_idx]
        v = path[edge_idx + 1]
        
        if u not in self._node_positions or v not in self._node_positions:
            return
        
        # Get positions of the two nodes
        x1, y1 = self._sc(*self._node_positions[u], W, H)
        x2, y2 = self._sc(*self._node_positions[v], W, H)
        
        # Interpolate jet position along the path
        jet_x = x1 + (x2 - x1) * edge_progress
        jet_y = y1 + (y2 - y1) * edge_progress
        
        # Calculate rotation angle based on direction of movement
        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx)
        
        # Draw jet as a triangle pointing in direction of travel
        jet_size = 12
        # Rotate the triangle to point in the direction of travel
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Triangle vertices (pointing right initially)
        vertices = [
            (jet_size, 0),          # front point
            (-jet_size * 0.6, jet_size * 0.6),
            (-jet_size * 0.6, -jet_size * 0.6),
        ]
        
        # Rotate and translate vertices
        rotated = []
        for vx, vy in vertices:
            rx = vx * cos_a - vy * sin_a + jet_x
            ry = vx * sin_a + vy * cos_a + jet_y
            rotated.extend([rx, ry])
        
        # Draw jet body
        c.create_polygon(rotated,
                        fill=C["cyan"], outline=C["pink"], width=2,
                        tags="jet")
        
        # Draw jet trail (glowing effect)
        glow_colors = [
            blend_with_bg(C["cyan"], 0.2),
            blend_with_bg(C["cyan"], 0.1),
        ]
        for i, glow_col in enumerate(glow_colors):
            glow_size = jet_size + (i + 1) * 8
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            glow_vertices = [(jet_size, 0),
                           (-jet_size * 0.6, jet_size * 0.6),
                           (-jet_size * 0.6, -jet_size * 0.6)]
            rotated_glow = []
            for vx, vy in glow_vertices:
                rx = vx * cos_a - vy * sin_a + jet_x
                ry = vx * sin_a + vy * cos_a + jet_y
                rotated_glow.extend([rx, ry])
            c.create_polygon(rotated_glow,
                           fill=glow_col, outline="",
                           tags="jet")

    def _draw_map_legend(self, c, W, H):
        metric = self.map_metric_var.get()
        metric_str = {"distance":"SHORTEST DISTANCE", "time":"FASTEST TIME", "fuel":"LOWEST FUEL"}[metric]
        items = [
            (C["cyan"],   "SHORTEST DISTANCE" if metric == "distance" else "—"),
            (C["green"],  "FASTEST TIME" if metric == "time" else "—"),
            (C["orange"], "LOWEST FUEL" if metric == "fuel" else "—"),
            (C["pink"],   "SOURCE NODE"),
            (C["cyan"],   "TARGET NODE (outline)"),
        ]
        lx = W - 260; ly = H - 150
        c.create_rectangle(lx-10, ly-16, W-8, H-8,
                           fill=C["panel"], outline=C["border"])
        c.create_text(lx+4, ly, text=f"LEGEND — {metric_str}", fill=C["textdim"],
                      font=("Courier New", 15, "bold"), anchor="w")
        for i,(col,label) in enumerate(items):
            yy = ly + 20 + i*20
            c.create_line(lx, yy+5, lx+22, yy+5, fill=col, width=3)
            c.create_text(lx+28, yy, text=label, fill=col,
                          font=("Courier New", 13), anchor="w")

    def _draw_map_results(self, c, W, H):
        """Draw the routes/results panels as overlays on the canvas like the legend."""
        if not hasattr(self, 'results'):
            return
        
        results = self.results
        configs = [
            ("distance", "SHORTEST DISTANCE", C["cyan"]),
            ("time",     "FASTEST TIME",      C["green"]),
            ("fuel",     "LOWEST FUEL",       C["orange"]),
        ]
        
        # Position results panels below legend on the left side
        rx = 14; ry = H - 520
        panel_width = 360
        panel_height = 142
        
        for i, (key, title, color) in enumerate(configs):
            r = results.get(key, {})
            path = r.get('path', [])
            
            # Panel background
            panel_y = ry + i * (panel_height + 8)
            c.create_rectangle(rx, panel_y, rx + panel_width, panel_y + panel_height,
                             fill=C["panel"], outline=color, width=2)
            
            # Title
            c.create_text(rx + 8, panel_y + 15, text=f"◈ {title}",
                         fill=color, font=("Courier New", 15, "bold"), anchor="nw")
            
            # Path display
            if path:
                path_str = " → ".join(path)
                # Wrap path text if too long
                if len(path_str) > 30:
                    path_str = " → ".join(path[:len(path)//2]) + "\n  → " + " → ".join(path[len(path)//2:])
                c.create_text(rx + 8, panel_y + 45, text=path_str,
                             fill=C["text"], font=("Courier New", 12), anchor="nw", width=panel_width-16)
            else:
                c.create_text(rx + 8, panel_y + 45, text="NO PATH",
                             fill=C["textdim"], font=("Courier New", 12), anchor="nw")
            
            # Stats line
            td = r.get('td', 0)
            tt = r.get('tt', 0)
            tf = r.get('tf', 0)
            stats_text = f"  {td:.0f}km  {tt:.0f}min  {tf:.1f}L"
            c.create_text(rx + 8, panel_y + 105, text=stats_text,
                         fill=color, font=("Courier New", 13, "bold"), anchor="nw")

    # ─────────────────────────────────────────
    #  TOOLTIP
    # ─────────────────────────────────────────
    def _on_canvas_motion(self, event):
        if self._drag_node:
            self._hide_tooltip()
            return
        if not hasattr(self,'_node_hit_areas'): return
        for node,(x,y) in self._node_hit_areas.items():
            if abs(event.x-x)<26 and abs(event.y-y)<26:
                self._show_tooltip(event, node); return
        self._hide_tooltip()

    def _show_tooltip(self, event, node):
        # If showing same node, just update position without recreating
        if self._tooltip_node == node and self._tooltip_win:
            x = self.canvas.winfo_rootx()+event.x+16
            y = self.canvas.winfo_rooty()+event.y+8
            self._tooltip_win.wm_geometry(f"+{x}+{y}")
            return
        
        # Different node, so destroy old tooltip and create new one
        self._hide_tooltip()
        info = [f"◈ {node}"]
        
        # Show outgoing edges (connections from this node)
        outgoing = []
        for v, attrs in self.graph.get(node, {}).items():
            outgoing.append(f"  →{v}: {attrs['distance']}km {attrs['time']}min {attrs['fuel']}L")
        
        # Show incoming edges (connections to this node)
        incoming = []
        for u in self.graph:
            if node in self.graph[u]:
                attrs = self.graph[u][node]
                incoming.append(f"  ←{u}: {attrs['distance']}km {attrs['time']}min {attrs['fuel']}L")
        
        # Combine both, with outgoing first, then incoming
        if outgoing:
            info.extend(outgoing)
        if incoming:
            info.extend(incoming)
        
        text = "\n".join(info)
        x = self.canvas.winfo_rootx()+event.x+16
        y = self.canvas.winfo_rooty()+event.y+8
        tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg=C["border"])
        tk.Label(tw, text=text, bg=C["panel"], fg=C["cyan"],
                 font=("Courier New",16), justify="left",
                 relief="flat", padx=8, pady=6).pack()
        self._tooltip_win = tw
        self._tooltip_node = node

    def _hide_tooltip(self, *_):
        if self._tooltip_win:
            try: self._tooltip_win.destroy()
            except: pass
            self._tooltip_win = None
        self._tooltip_node = None

    # ─────────────────────────────────────────
    #  PATH ANIMATION
    # ─────────────────────────────────────────
    def _animate_paths(self):
        if not hasattr(self,'results'): return
        
        if self._animation_running and self._anim_job:
            self.after_cancel(self._anim_job)
        
        self._animation_running = True
        duration = 8000 
        start = time.time()*1000

        def step():
            if not self._animation_running:
                return
            elapsed = time.time()*1000 - start
            t = elapsed / duration
            
            t = t % 1.0
            
            t_ease = 1-(1-t)**3
            for k in self._path_anim_progress:
                self._path_anim_progress[k] = t_ease
            
            self._jet_progress = t
            
            self._redraw_map()
            self._anim_job = self.after(16, step)
        self._anim_job = self.after(0, step)

    # ─────────────────────────────────────────
    #  BACKGROUND ANIMATION
    # ─────────────────────────────────────────
    def _start_bg_anim(self):
        self._particles = [
            {"x": random.random(), "y": random.random(),
             "vx": (random.random()-0.5)*0.0003,
             "vy": (random.random()-0.5)*0.0003,
             "r": random.uniform(1,2.5),
             "col": blend_with_bg(*random.choice([
                 (C["cyan"], 0.27),
                 (C["purple"], 0.20),
                 (C["pink"], 0.13),
             ])) }
            for _ in range(40)
        ]
        self._pulse = 0
        self._tick_anim()

    def _tick_anim(self):
        c = self.canvas
        if not c.winfo_exists(): return
        self._pulse = (self._pulse+0.05)%( 2*math.pi)
        
        # Blink the bidirectional button highlight
        self._bidir_blink_phase = (self._bidir_blink_phase + 0.05) % 1.0
        if self._bidir_blink_phase < 0.5:
            # Bright mode
            self.bidir_btn.config(fg=C["cyan"], highlightcolor=C["cyan"])
        else:
            # Normal mode
            self.bidir_btn.config(fg=C["purple"], highlightcolor=C["purple"])
        
        self.after(50, self._tick_anim)

    # ─────────────────────────────────────────
    #  DEBUG TAB
    # ─────────────────────────────────────────
    def _refresh_debug(self):
        if not hasattr(self,'results'): return
        metric = self.dbg_metric.get()
        r = self.results.get(metric,{})
        steps = r.get('steps',[])
        path  = r.get('path',[])

        lb = self.steps_listbox
        lb.delete(0,"end")
        self._debug_steps = steps

        for i,s in enumerate(steps):
            if 'visit' in s:
                d_val = s['dist_so_far']
                d_str = f"{d_val:.1f}" if d_val!=float('inf') else "∞"
                lb.insert("end", f"  [{i:02d}] VISIT   {s['visit']:<12}  cost={d_str}")
                lb.itemconfig("end", fg=C["cyan"])
            elif 'relax' in s:
                u,v = s['relax']
                lb.insert("end", f"  [{i:02d}] RELAX   {u}→{v:<8}  new={s['new_dist']:.1f}")
                lb.itemconfig("end", fg=C["yellow"])

        td,tt,tf = r.get('td',0),r.get('tt',0),r.get('tf',0)
        arrow = " → ".join(path) if path else "NO PATH"
        self._write_debug_summary(
            f"METRIC: {metric.upper()}   PATH: {arrow}\n"
            f"TOTAL STEPS: {len(steps)}   DIST: {td:.0f}km   TIME: {tt:.0f}min   FUEL: {tf:.1f}L\n"
            f"VISITED NODES: {sum(1 for s in steps if 'visit' in s)}   "
            f"RELAXATIONS: {sum(1 for s in steps if 'relax' in s)}"
        )

        if steps:
            lb.select_set(0)
            self._on_step_select(None)

    def _on_step_select(self, event):
        lb = self.steps_listbox
        sel = lb.curselection()
        if not sel: return
        idx = sel[0]
        if not hasattr(self,'_debug_steps'): return
        steps = self._debug_steps
        if idx >= len(steps): return
        s = steps[idx]

        dist_table = s.get('dist_table',{})
        prev_table = s.get('prev_table',{})
        visited_so_far = set()
        for ss in steps[:idx+1]:
            if 'visit' in ss:
                visited_so_far.add(ss['visit'])

        tree = self.dbg_tree
        tree.delete(*tree.get_children())

        metric = self.dbg_metric.get()
        unit = {'distance':'km','time':'min','fuel':'L'}[metric]

        active_u = active_v = None
        if 'relax' in s:
            active_u, active_v = s['relax']

        for node in sorted(dist_table.keys()):
            d = dist_table[node]
            p = prev_table.get(node)
            d_str = f"{d:.1f} {unit}" if d!=float('inf') else "∞"
            p_str = p if p else "—"
            status = "VISITED" if node in visited_so_far else (
                     "QUEUED"  if d<float('inf') else "UNVISITED")

            tag = ""
            if 'visit' in s and s['visit']==node: tag="visit"
            elif 'relax' in s and s['relax'][1]==node: tag="relax"

            iid = tree.insert("","end",values=(node,d_str,p_str,status))
            if tag=="visit":
                tree.item(iid, tags=("visit",))
            elif tag=="relax":
                tree.item(iid, tags=("relax",))
            elif status=="VISITED":
                tree.item(iid, tags=("done",))

        tree.tag_configure("visit", foreground=C["cyan"])
        tree.tag_configure("relax", foreground=C["yellow"])
        tree.tag_configure("done",  foreground=C["textdim"])

        # ── Arithmetic computation panel ──────
        self._update_arith(s, metric, unit, dist_table, prev_table)

    def _update_arith(self, s, metric, unit, dist_table, prev_table):
        """Show the arithmetic behind the current step."""
        lines = []
        if 'visit' in s:
            node = s['visit']
            d = s['dist_so_far']
            d_str = f"{d:.2f}" if d != float('inf') else "∞"
            lines.append(f"  VISIT  ──  Node: {node}")
            lines.append(f"  Current shortest dist to {node} = {d_str} {unit}")
            lines.append(f"  (Popped from priority queue as minimum-cost node)")
        elif 'relax' in s:
            u, v = s['relax']
            new_d = s['new_dist']
            old_d = dist_table.get(v, float('inf'))
            # dist[u] = new_d - edge weight
            edge_w = None
            if hasattr(self, 'graph') and u in self.graph and v in self.graph[u]:
                edge_w = self.graph[u][v][metric]
            dist_u = new_d - (edge_w if edge_w is not None else 0)
            prev_d_str = f"{old_d:.2f}" if old_d != float('inf') else "∞"
            if edge_w is not None:
                lines.append(f"  RELAX  ──  Edge: {u} → {v}")
                lines.append(f"  dist[{u}] + w({u}→{v}) < dist[{v}]?")
                lines.append(f"  {dist_u:.2f} + {edge_w:.2f} = {new_d:.2f} {unit}  <  {prev_d_str} {unit}  ✔ UPDATE")
                lines.append(f"  dist[{v}] updated: {prev_d_str}  →  {new_d:.2f} {unit}")
                lines.append(f"  prev[{v}] set to: {u}")
            else:
                lines.append(f"  RELAX  ──  Edge: {u} → {v}")
                lines.append(f"  New dist[{v}] = {new_d:.2f} {unit}")

        text = "\n".join(lines) if lines else "  — Select a step to see arithmetic —"
        t = self.arith_text
        t.config(state="normal")
        t.delete("1.0","end")
        t.insert("end", text)
        t.config(state="disabled")

    def _write_debug_summary(self, text):
        t = self.dbg_summary
        t.config(state="normal")
        t.delete("1.0","end")
        t.insert("end", text)
        t.config(state="disabled")

    # ─────────────────────────────────────────
    #  STATUS
    # ─────────────────────────────────────────
    def _set_status(self, msg, color):
        self.status_lbl.config(text=msg, fg=color)

    def _disable_inputs(self):
        """Disable all input controls while computing."""
        self.src_cb.config(state="disabled")
        self.dst_cb.config(state="disabled")
        self.bidir_btn.config(state="disabled")
        for btn in [b for b in self.winfo_children() if isinstance(b, tk.Button)]:
            btn.config(state="disabled")

    def _enable_inputs(self):
        """Re-enable all input controls after computing."""
        self.src_cb.config(state="readonly")
        self.dst_cb.config(state="readonly")
        self.bidir_btn.config(state="normal")
        for btn in [b for b in self.winfo_children() if isinstance(b, tk.Button)]:
            btn.config(state="normal")


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
