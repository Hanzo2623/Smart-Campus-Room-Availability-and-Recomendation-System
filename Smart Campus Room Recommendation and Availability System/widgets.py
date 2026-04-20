# ============================================================
# widgets.py  –  Reusable tkinter widget helpers
# Smart Campus Room Availability and Recommendation System
# ============================================================

import tkinter as tk
from tkinter import ttk
from theme import (
    BG_INPUT, BG_PANEL, BG_CARD,
    ACCENT, ACCENT_DARK, ACCENT_ALT,
    TEXT_WHITE, TEXT_MUTED, BORDER, SUCCESS, DANGER,
    FONT_BODY, FONT_BTN, FONT_SMALL,
    CARD_PX, CARD_PY,
    PAD_XS, PAD_SM, PAD_MD, PAD_LG,
    LABEL_W_PX, FIELD_W_PX, ROW_PY, BTN_GAP,
)


# ────────────────────────────────────────────────────────────
# Basic atoms
# ────────────────────────────────────────────────────────────

def styled_entry(parent, placeholder: str) -> tk.Entry:
    """Entry with placeholder text. Width is driven by the grid column."""
    ent = tk.Entry(
        parent, font=FONT_BODY,
        bg=BG_INPUT, fg=TEXT_MUTED,
        insertbackground=TEXT_WHITE,
        relief="flat", bd=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        width=30,
    )
    ent.insert(0, placeholder)
    ent._ph = placeholder

    def _in(_):
        if ent.get() == placeholder:
            ent.delete(0, "end")
            ent.config(fg=TEXT_WHITE)

    def _out(_):
        if not ent.get():
            ent.insert(0, placeholder)
            ent.config(fg=TEXT_MUTED)

    ent.bind("<FocusIn>",  _in)
    ent.bind("<FocusOut>", _out)
    return ent


def styled_combobox(parent, textvariable, values) -> ttk.Combobox:
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "App.TCombobox",
        fieldbackground=BG_INPUT, background=BG_INPUT,
        foreground=TEXT_WHITE,
        selectbackground=ACCENT, selectforeground=TEXT_WHITE,
        borderwidth=0, padding=5,
    )
    style.map(
        "App.TCombobox",
        fieldbackground=[("readonly", BG_INPUT)],
        foreground=[("readonly", TEXT_WHITE)],
    )
    return ttk.Combobox(
        parent, textvariable=textvariable, values=values,
        font=FONT_BODY, state="readonly", style="App.TCombobox",
    )


def styled_button(parent, text, cmd, color=ACCENT) -> tk.Button:
    hover = ACCENT_DARK if color == ACCENT else "#444466"
    btn = tk.Button(
        parent, text=text, command=cmd,
        font=FONT_BTN, fg=TEXT_WHITE, bg=color,
        relief="flat", bd=0,
        width=0, pady=9,
        activebackground=hover, activeforeground=TEXT_WHITE,
        cursor="hand2",
    )
    btn.bind("<Enter>", lambda _: btn.config(bg=hover))
    btn.bind("<Leave>", lambda _: btn.config(bg=color))
    return btn


def divider(parent, color=BORDER) -> tk.Frame:
    return tk.Frame(parent, bg=color, height=1)


def full_card(parent, **kw) -> tk.Frame:
    """Full-width card that fills the content area horizontally."""
    c = tk.Frame(
        parent, bg=BG_PANEL,
        padx=kw.pop("padx", CARD_PX),
        pady=kw.pop("pady", CARD_PY),
        **kw,
    )
    c.pack(fill="both", expand=True, pady=(0, PAD_SM), padx=PAD_MD)
    return c


def clear(frame: tk.Frame) -> None:
    """Destroy all child widgets inside frame."""
    for w in frame.winfo_children():
        w.destroy()


def get_val(ent: tk.Entry) -> str:
    """Return entry text, treating the placeholder as empty string."""
    v = ent.get()
    return "" if v == getattr(ent, "_ph", None) else v


# ────────────────────────────────────────────────────────────
# Composite form builders
# ────────────────────────────────────────────────────────────

def build_form(card_frame: tk.Frame, rows: list) -> tuple:
    """
    Build a centred label | entry grid inside card_frame.

    Parameters
    ----------
    card_frame : tk.Frame
        The parent card to place the form inside.
    rows : list of (label_text, placeholder_text) tuples

    Returns
    -------
    (entries_dict, wrapper_frame)
        entries_dict  – {label_text: tk.Entry}
        wrapper_frame – the sub-frame holding the grid (so buttons can
                        be placed inside it at a specific grid row)
    """
    wrapper = tk.Frame(card_frame, bg=BG_PANEL)
    wrapper.pack(anchor="center", pady=(PAD_XS, 0))
    wrapper.columnconfigure(0, minsize=LABEL_W_PX, weight=0)
    wrapper.columnconfigure(1, minsize=FIELD_W_PX, weight=1)

    entries = {}
    for row_i, (lbl_text, placeholder) in enumerate(rows):
        tk.Label(
            wrapper, text=lbl_text, font=FONT_BODY,
            fg=TEXT_MUTED, bg=BG_PANEL, anchor="e",
        ).grid(row=row_i, column=0,
               sticky="e", padx=(0, PAD_MD), pady=ROW_PY)

        ent = styled_entry(wrapper, placeholder)
        ent.grid(row=row_i, column=1,
                 sticky="ew", pady=ROW_PY, ipady=5)
        entries[lbl_text] = ent

    return entries, wrapper


def build_btn_row(wrapper: tk.Frame, buttons: list, grid_row: int) -> tk.Frame:
    """
    Row of uniform buttons placed inside the same wrapper as the form rows.

    buttons : list of (label, command, color) tuples
    """
    frame = tk.Frame(wrapper, bg=BG_PANEL)
    frame.grid(row=grid_row, column=1,
               sticky="w", pady=(PAD_MD, PAD_XS))
    for i, (lbl, cmd, col) in enumerate(buttons):
        btn = styled_button(frame, lbl, cmd, color=col)
        btn.pack(side="left", padx=(0 if i == 0 else BTN_GAP, 0))
    return frame


def build_feedback(wrapper: tk.Frame, grid_row: int) -> tk.Label:
    """Feedback label aligned under the entry column."""
    lbl = tk.Label(
        wrapper, text="", font=FONT_BODY,
        bg=BG_PANEL, fg=SUCCESS,
        anchor="w", wraplength=FIELD_W_PX, justify="left",
    )
    lbl.grid(row=grid_row, column=1, sticky="w", pady=(PAD_XS, 0))
    return lbl
