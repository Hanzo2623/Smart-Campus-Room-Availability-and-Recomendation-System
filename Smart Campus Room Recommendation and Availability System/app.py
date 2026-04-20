# ============================================================
# app.py  –  All application screens (SmartCampusApp + pages)
# Smart Campus Room Availability and Recommendation System
# ============================================================

import tkinter as tk
from theme import (
    BG_DARK, BG_PANEL, BG_CARD,
    ACCENT, ACCENT_ALT, SUCCESS, DANGER,
    TEXT_WHITE, TEXT_MUTED,
    FONT_TITLE, FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_MONO,
    PAD_XS, PAD_SM, PAD_MD, PAD_LG,
    BTN_GAP,
)
from widgets import (
    styled_button, styled_combobox,
    divider, full_card, clear, get_val,
    build_form, build_feedback,
)
from logic import (
    rooms, add_schedule, check_availability,
    recommend_room, display_summary,
)
import file_handler


# ────────────────────────────────────────────────────────────
# Main application window
# ────────────────────────────────────────────────────────────

class SmartCampusApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Campus Room Availability & Recommendation System")
        self.root.geometry("820x600")
        self.root.minsize(600, 500)
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        self._active_nav = None

        self._build_header()
        self._build_sidebar()
        self._build_content()
        self._build_statusbar()
        self.show_summary()

    # ── Chrome ──────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=58)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="🏫  Smart Campus Room System",
            font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL,
        ).pack(side="left", padx=PAD_LG, pady=PAD_MD)
        tk.Label(
            hdr, text="BatStateU · CC 102",
            font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_PANEL,
        ).pack(side="right", padx=PAD_LG)
        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x")

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=BG_PANEL, width=210)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar, text="NAVIGATION", font=FONT_SMALL,
            fg=TEXT_MUTED, bg=BG_PANEL,
        ).pack(anchor="w", padx=PAD_LG, pady=(PAD_LG, PAD_SM))

        nav = [
            ("📋   View Summary",        self.show_summary),
            ("➕   Add Schedule",        self.show_add_schedule),
            ("🔍   Check Availability",  self.show_check_availability),
            ("⭐   Recommend Room",      self.show_recommend_room),
            ("📁   Records",             self.show_records),   # ← new (file handling)
        ]
        self._nav_btns = []
        for lbl, cmd in nav:
            b = tk.Button(
                self.sidebar, text=lbl, font=FONT_BODY,
                fg=TEXT_WHITE, bg=BG_PANEL,
                relief="flat", anchor="w",
                padx=PAD_LG, pady=10,
                activebackground=BG_CARD, activeforeground=ACCENT,
                cursor="hand2",
            )
            b.config(command=lambda c=cmd, btn=b: self._nav(c, btn))
            b.pack(fill="x", padx=PAD_SM, pady=2)
            b.bind("<Enter>",
                   lambda e, btn=b: btn.config(bg=BG_CARD, fg=ACCENT)
                   if btn is not self._active_nav else None)
            b.bind("<Leave>",
                   lambda e, btn=b: btn.config(
                       bg=BG_CARD  if btn is self._active_nav else BG_PANEL,
                       fg=ACCENT   if btn is self._active_nav else TEXT_WHITE,
                   ))
            self._nav_btns.append(b)

        divider(self.sidebar).pack(fill="x", padx=PAD_LG, pady=PAD_MD)
        self._count_var = tk.StringVar()
        tk.Label(
            self.sidebar, textvariable=self._count_var,
            font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_PANEL, anchor="w",
        ).pack(anchor="w", padx=PAD_LG)
        self._refresh_count()

    def _nav(self, cmd, btn):
        if self._active_nav:
            self._active_nav.config(bg=BG_PANEL, fg=TEXT_WHITE)
        btn.config(bg=BG_CARD, fg=ACCENT)
        self._active_nav = btn
        cmd()

    def _build_content(self):
        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill="both", expand=True, side="right")

        self.canvas = tk.Canvas(outer, bg=BG_DARK, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)

        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.container = tk.Frame(self.canvas, bg=BG_DARK)
        self._wid = self.canvas.create_window(
            (0, 0), window=self.container, anchor="n"
        )
        self.container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        def _resize(e):
            max_width = 900
            width = min(e.width, max_width)
            x = (e.width - width) // 2
            self.canvas.itemconfig(self._wid, width=width)
            self.canvas.coords(self._wid, x, 0)

        self.canvas.bind("<Configure>", _resize)
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            ),
        )
        self.content = self.container

    def _build_statusbar(self):
        divider(self.root).pack(fill="x", side="bottom")
        self._status = tk.StringVar(value="Ready.")
        tk.Label(
            self.root, textvariable=self._status,
            font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_PANEL,
            anchor="w", padx=PAD_MD, pady=PAD_SM,
        ).pack(fill="x", side="bottom")

    def _st(self, msg):
        self._status.set(msg)

    def _refresh_count(self):
        self._count_var.set(f"Rooms in system: {len(rooms)}")

    def _page_title(self, text):
        tk.Label(
            self.content, text=text, font=FONT_TITLE,
            fg=TEXT_WHITE, bg=BG_DARK, anchor="w",
        ).pack(fill="x", pady=(0, PAD_MD))

    # ── Page: Summary ────────────────────────────────────────

    def show_summary(self):
        clear(self.content)
        self._st("Showing all rooms and schedules.")
        self._page_title("Room Summary")

        data = display_summary()
        if not data:
            tk.Label(
                self.content,
                text="No rooms yet. Use 'Add Schedule' to get started.",
                font=FONT_BODY, fg=TEXT_MUTED, bg=BG_DARK,
            ).pack(pady=PAD_LG)
            return

        for room in data:
            c = full_card(self.content)
            hrow = tk.Frame(c, bg=BG_PANEL)
            hrow.pack(fill="x")
            tk.Label(
                hrow, text=f"🚪  {room['name']}",
                font=FONT_HEAD, fg=ACCENT, bg=BG_PANEL, anchor="w",
            ).pack(side="left")
            tk.Label(
                hrow, text=f"Capacity: {room['capacity']} seats",
                font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_PANEL, anchor="e",
            ).pack(side="right")
            divider(c).pack(fill="x", pady=(PAD_SM, PAD_SM))
            for icon, key, col in [
                ("🛠", "features",  TEXT_WHITE),
                ("🕐", "schedules", SUCCESS),
            ]:
                row = tk.Frame(c, bg=BG_PANEL)
                row.pack(fill="x", pady=(0, PAD_XS))
                tk.Label(
                    row, text=icon, font=FONT_BODY,
                    fg=TEXT_MUTED, bg=BG_PANEL, width=3, anchor="w",
                ).pack(side="left")
                tk.Label(
                    row, text=room[key], font=FONT_BODY,
                    fg=col, bg=BG_PANEL, anchor="w",
                    wraplength=750, justify="left",
                ).pack(side="left", fill="x")

    # ── Page: Add Schedule ───────────────────────────────────

    def show_add_schedule(self):
        clear(self.content)
        self._st("Add a new room or append a time slot.")
        self._page_title("Add Room Schedule")

        c = full_card(self.content)
        entries, wrapper = build_form(c, [
            ("Room Name", "e.g.  Room 101"),
            ("Capacity",  "e.g.  30"),
            ("Features",  "e.g.  projector, whiteboard"),
            ("Time Slot", "e.g.  08:00-09:00"),
        ])
        feedback = build_feedback(wrapper, grid_row=4)

        btn_frame = tk.Frame(wrapper, bg=BG_PANEL)
        btn_frame.grid(row=5, column=1, sticky="w", pady=(PAD_SM, PAD_XS))

        def _submit():
            room = get_val(entries["Room Name"])
            slot = get_val(entries["Time Slot"])
            ok, msg = add_schedule(
                room,
                get_val(entries["Capacity"]),
                get_val(entries["Features"]),
                slot,
            )
            feedback.config(
                text=("✅  " if ok else "⚠️  ") + msg,
                fg=SUCCESS if ok else DANGER,
            )
            if ok:
                # ── File handling: log this reservation ──────
                from logic import current_user
                file_handler.log_reservation(
                    current_user["name"],
                    current_user["role"],
                    room,
                    slot,
                )
                # ─────────────────────────────────────────────
                self._refresh_count()
                self._st("Schedule added.")
            else:
                self._st("Could not add schedule.")

        for i, (lbl, cmd, col) in enumerate([
            ("Add Schedule", _submit,           ACCENT),
            ("View Summary", self.show_summary, ACCENT_ALT),
        ]):
            styled_button(btn_frame, lbl, cmd, color=col).pack(
                side="left", padx=(0 if i == 0 else BTN_GAP, 0)
            )

        tc = full_card(self.content)
        tk.Label(
            tc, text="💡  Tips", font=FONT_HEAD,
            fg=ACCENT, bg=BG_PANEL, anchor="w",
        ).pack(fill="x", pady=(0, PAD_SM))
        for tip in [
            "If the room already exists, only the new time slot is added.",
            "Time slots must be in HH:MM-HH:MM (24-hour) format.",
            "Overlapping time slots are automatically rejected.",
            "Features are ignored when appending to an existing room.",
        ]:
            tk.Label(
                tc, text=f"   •  {tip}", font=FONT_SMALL,
                fg=TEXT_MUTED, bg=BG_PANEL, anchor="w",
            ).pack(fill="x", pady=2)

    # ── Page: Check Availability ─────────────────────────────

    def show_check_availability(self):
        clear(self.content)
        self._st("Check whether a room is free at a given time.")
        self._page_title("Check Room Availability")

        c = full_card(self.content)
        entries, wrapper = build_form(c, [
            ("Select Room", ""),
            ("Time Slot",   "e.g.  08:00-09:00"),
        ])

        room_var   = tk.StringVar()
        room_names = list(rooms.keys()) or ["No rooms available"]
        dd = styled_combobox(wrapper, room_var, room_names)
        dd.grid(row=0, column=1, sticky="ew", pady=(PAD_SM, PAD_SM), ipady=4)
        if room_names:
            dd.current(0)

        slot_ent  = entries["Time Slot"]
        btn_frame = tk.Frame(wrapper, bg=BG_PANEL)
        btn_frame.grid(row=2, column=1, sticky="w", pady=(PAD_MD, PAD_XS))

        result_card = full_card(self.content, pady=PAD_MD)
        r_icon = tk.Label(result_card, text="", font=("Helvetica", 28), bg=BG_PANEL)
        r_icon.pack()
        r_lbl  = tk.Label(
            result_card, text="", font=FONT_HEAD,
            bg=BG_PANEL, fg=TEXT_WHITE, wraplength=700, justify="center",
        )
        r_lbl.pack(pady=(PAD_SM, 0))

        def _check():
            ok, msg = check_availability(room_var.get(), get_val(slot_ent))
            result_card.pack(fill="x", pady=(0, PAD_SM))
            bg = "#1a3a2a" if ok else "#3a1a1a"
            result_card.config(bg=bg)
            r_icon.config(text="✅" if ok else "🔴", bg=bg)
            r_lbl.config(text=msg, fg=SUCCESS if ok else DANGER, bg=bg)
            self._st(msg)

        styled_button(btn_frame, "Check Availability", _check).pack(side="left")

    # ── Page: Recommend Room ─────────────────────────────────

    def show_recommend_room(self):
        clear(self.content)
        self._st("Find the best room for your requirements.")
        self._page_title("Recommend Best Room")

        c = full_card(self.content)
        entries, wrapper = build_form(c, [
            ("Number of Users",     "e.g.  25"),
            ("Required Feature",    "e.g.  projector  (optional)"),
            ("Requested Time Slot", "e.g.  09:00-10:00"),
        ])

        results_frame = tk.Frame(self.content, bg=BG_DARK)

        def _recommend():
            clear(results_frame)
            results_frame.pack(fill="x")

            best, msg, candidates = recommend_room(
                get_val(entries["Number of Users"]),
                get_val(entries["Required Feature"]),
                get_val(entries["Requested Time Slot"]),
            )

            banner = full_card(results_frame)
            if best:
                tk.Label(
                    banner, text="⭐  Top Recommendation",
                    font=FONT_HEAD, fg=ACCENT, bg=BG_PANEL, anchor="w",
                ).pack(fill="x", pady=(0, PAD_SM))
                bd = rooms[best]
                for key, val in [
                    ("Room",      best),
                    ("Capacity",  f"{bd['capacity']} seats"),
                    ("Features",  ", ".join(bd["features"])),
                    ("Schedules", ", ".join(bd["schedules"]) or "None"),
                ]:
                    row = tk.Frame(banner, bg=BG_PANEL)
                    row.pack(fill="x", pady=2)
                    tk.Label(
                        row, text=key, font=FONT_BODY,
                        fg=TEXT_MUTED, bg=BG_PANEL, width=10, anchor="w",
                    ).pack(side="left")
                    tk.Label(
                        row, text=f":  {val}", font=FONT_BODY,
                        fg=TEXT_WHITE, bg=BG_PANEL, anchor="w",
                    ).pack(side="left")
                self._st(f"Recommended: {best}")
            else:
                tk.Label(
                    banner, text=f"⚠️  {msg}", font=FONT_BODY,
                    fg=DANGER, bg=BG_PANEL, anchor="w",
                ).pack(fill="x")
                self._st("No suitable room found.")

            if candidates:
                tk.Label(
                    results_frame, text="All Matching Rooms (Ranked)",
                    font=FONT_HEAD, fg=ACCENT, bg=BG_DARK, anchor="w",
                ).pack(fill="x", pady=(PAD_MD, PAD_SM))

                tbl = tk.Frame(results_frame, bg=BG_CARD)
                tbl.pack(fill="x", pady=(0, PAD_SM))

                col_spec = [
                    ("Rank",     0,  55),
                    ("Room",     1, 155),
                    ("Score",    0,  65),
                    ("Capacity", 0,  90),
                    ("Features", 2, 200),
                ]

                def _cfg(f):
                    for i, (_, wt, mn) in enumerate(col_spec):
                        f.columnconfigure(i, weight=wt, minsize=mn)

                hf = tk.Frame(tbl, bg=BG_CARD)
                hf.pack(fill="x", padx=PAD_MD, pady=(PAD_SM, PAD_XS))
                _cfg(hf)
                for i, (title, *_) in enumerate(col_spec):
                    tk.Label(
                        hf, text=title, font=FONT_SMALL,
                        fg=TEXT_MUTED, bg=BG_CARD, anchor="w",
                    ).grid(row=0, column=i, sticky="ew")

                divider(tbl).pack(fill="x", padx=PAD_MD)

                for rank, (rname, score, cap, feats) in enumerate(candidates, 1):
                    rbg  = BG_PANEL if rank == 1 else BG_CARD
                    rcol = ACCENT   if rank == 1 else TEXT_WHITE
                    drow = tk.Frame(tbl, bg=rbg)
                    drow.pack(fill="x", padx=PAD_MD, pady=2)
                    _cfg(drow)
                    for i, val in enumerate([
                        f"#{rank}", rname, str(score),
                        f"{cap} seats", ", ".join(feats)
                    ]):
                        tk.Label(
                            drow, text=val, font=FONT_SMALL,
                            fg=rcol, bg=rbg, anchor="w",
                        ).grid(row=0, column=i,
                               sticky="ew", padx=(0, PAD_SM))

        btn_frame = tk.Frame(wrapper, bg=BG_PANEL)
        btn_frame.grid(row=len(entries), column=1,
                       sticky="w", pady=(PAD_MD, PAD_XS))
        styled_button(btn_frame, "Find Best Room", _recommend).pack(side="left")

        kc = full_card(self.content)
        tk.Label(
            kc, text="📊  Scoring Key", font=FONT_HEAD,
            fg=ACCENT, bg=BG_PANEL, anchor="w",
        ).pack(fill="x", pady=(0, PAD_SM))
        for tag, desc in [
            ("+15", "Base score for every available room"),
            ("+5 ", "Room has the required feature"),
            ("−n ", "Small penalty per 10 excess seats (caps at −5)"),
        ]:
            row = tk.Frame(kc, bg=BG_PANEL)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text=tag, font=FONT_MONO,
                fg=ACCENT, bg=BG_PANEL, width=5, anchor="w",
            ).pack(side="left")
            tk.Label(
                row, text=desc, font=FONT_SMALL,
                fg=TEXT_MUTED, bg=BG_PANEL, anchor="w",
            ).pack(side="left")

    # ── Page: Records (file handling viewer) ─────────────────

    def show_records(self):
        """
        Manager view: display users_log.csv and reservations_log.csv
        in two tabbed tables.  A 'Clear' button is provided for each.
        """
        clear(self.content)
        self._st("Viewing system records (file logs).")
        self._page_title("📁  System Records")

        # ── User log ─────────────────────────────────────────
        uc = full_card(self.content)
        tk.Label(
            uc, text="👤  User Login Log", font=FONT_HEAD,
            fg=ACCENT, bg=BG_PANEL, anchor="w",
        ).pack(fill="x", pady=(0, PAD_SM))

        self._render_table(
            uc,
            headers=["Name", "Role", "Login Time"],
            rows=file_handler.read_users(),
            empty_msg="No users have logged in yet.",
        )

        def _clear_users():
            file_handler.clear_users()
            self.show_records()
            self._st("User log cleared.")

        styled_button(uc, "🗑  Clear User Log", _clear_users,
                      color="#555577").pack(anchor="e", pady=(PAD_SM, 0))

        # ── Reservation log ───────────────────────────────────
        rc = full_card(self.content)
        tk.Label(
            rc, text="🏷  Room Reservation Log", font=FONT_HEAD,
            fg=ACCENT, bg=BG_PANEL, anchor="w",
        ).pack(fill="x", pady=(0, PAD_SM))

        self._render_table(
            rc,
            headers=["Name", "Role", "Room", "Time Slot", "Reserved At"],
            rows=file_handler.read_reservations(),
            empty_msg="No reservations have been made yet.",
        )

        def _clear_res():
            file_handler.clear_reservations()
            self.show_records()
            self._st("Reservation log cleared.")

        styled_button(rc, "🗑  Clear Reservation Log", _clear_res,
                      color="#555577").pack(anchor="e", pady=(PAD_SM, 0))

    def _render_table(self, parent, headers: list, rows: list,
                      empty_msg: str):
        """Generic table renderer used by show_records()."""
        if not rows:
            tk.Label(
                parent, text=empty_msg, font=FONT_SMALL,
                fg=TEXT_MUTED, bg=BG_PANEL, anchor="w",
            ).pack(fill="x", pady=(0, PAD_SM))
            return

        tbl = tk.Frame(parent, bg=BG_CARD)
        tbl.pack(fill="x", pady=(0, PAD_SM))

        col_count = len(headers)
        for i in range(col_count):
            tbl.columnconfigure(i, weight=1)

        # Header row
        hf = tk.Frame(tbl, bg=BG_CARD)
        hf.pack(fill="x", padx=PAD_MD, pady=(PAD_SM, PAD_XS))
        for i, h in enumerate(headers):
            for j in range(col_count):
                hf.columnconfigure(j, weight=1)
            tk.Label(
                hf, text=h, font=FONT_SMALL,
                fg=TEXT_MUTED, bg=BG_CARD, anchor="w",
            ).grid(row=0, column=i, sticky="ew", padx=(0, PAD_SM))

        divider(tbl).pack(fill="x", padx=PAD_MD)

        for idx, row in enumerate(rows):
            rbg  = BG_PANEL if idx % 2 == 0 else BG_CARD
            drow = tk.Frame(tbl, bg=rbg)
            drow.pack(fill="x", padx=PAD_MD, pady=1)
            for j in range(col_count):
                drow.columnconfigure(j, weight=1)
            for j, h in enumerate(headers):
                tk.Label(
                    drow, text=row.get(h, ""),
                    font=FONT_SMALL, fg=TEXT_WHITE, bg=rbg, anchor="w",
                ).grid(row=0, column=j, sticky="ew", padx=(0, PAD_SM), pady=3)
