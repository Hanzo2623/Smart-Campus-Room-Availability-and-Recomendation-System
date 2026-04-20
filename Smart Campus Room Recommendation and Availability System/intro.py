# ============================================================
# intro.py  –  Welcome / login screen
# Smart Campus Room Availability and Recommendation System
# ============================================================

import tkinter as tk
from theme import (
    BG_DARK, BG_PANEL,
    TEXT_WHITE, TEXT_MUTED,
    FONT_TITLE, FONT_BODY,
    LABEL_W_PX, FIELD_W_PX, ROW_PY,
    PAD_MD,
)
from widgets import styled_entry, styled_combobox, styled_button, get_val
import file_handler
from logic import current_user
from app import SmartCampusApp


class IntroScreen:
    """
    First screen the user sees.  Collects name and role, then:
      1. Logs the login to users_log.csv via file_handler.
      2. Stores name/role in logic.current_user for use when
         logging reservations later.
      3. Launches SmartCampusApp.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.configure(bg=BG_DARK)

        self.frame = tk.Frame(root, bg=BG_DARK)
        self.frame.pack(fill="both", expand=True)

        card = tk.Frame(self.frame, bg=BG_PANEL, padx=40, pady=40)
        card.pack(expand=True)

        tk.Label(
            card, text="Welcome to Smart Campus System",
            font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL,
        ).pack(pady=(0, 20))

        wrapper = tk.Frame(card, bg=BG_PANEL)
        wrapper.pack()
        wrapper.columnconfigure(0, minsize=LABEL_W_PX)
        wrapper.columnconfigure(1, minsize=FIELD_W_PX)

        # Name field
        tk.Label(
            wrapper, text="Name", font=FONT_BODY,
            fg=TEXT_MUTED, bg=BG_PANEL, anchor="e",
        ).grid(row=0, column=0, padx=(0, PAD_MD), pady=ROW_PY)

        self.name_entry = styled_entry(wrapper, "Enter your name")
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=ROW_PY, ipady=5)

        # Role dropdown
        tk.Label(
            wrapper, text="Role", font=FONT_BODY,
            fg=TEXT_MUTED, bg=BG_PANEL, anchor="e",
        ).grid(row=1, column=0, padx=(0, PAD_MD), pady=ROW_PY)

        self.role_var = tk.StringVar()
        role_box = styled_combobox(wrapper, self.role_var, ["Student", "Teacher"])
        role_box.grid(row=1, column=1, sticky="ew", pady=ROW_PY, ipady=4)
        role_box.current(0)

        styled_button(card, "Enter System", self.enter_system).pack(pady=(20, 0))

    def enter_system(self):
        name = get_val(self.name_entry)
        role = self.role_var.get()

        if not name:
            name = "Anonymous"

        # ── File handling: log this login ────────────────────
        file_handler.log_user(name, role)

        # ── Store for later use when logging reservations ────
        current_user["name"] = name
        current_user["role"] = role

        self.frame.destroy()
        SmartCampusApp(self.root)
