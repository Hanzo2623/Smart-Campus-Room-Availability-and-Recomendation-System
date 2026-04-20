# ============================================================
# main.py  –  Entry point
# Smart Campus Room Availability and Recommendation System
# Course: CC 102 – Advanced Computer Programming
# Batangas State University – CICS
# ============================================================

import tkinter as tk
from logic import initialize_sample_data
from intro import IntroScreen


def main():
    initialize_sample_data()

    root = tk.Tk()
    root.title("Smart Campus Room Availability & Recommendation System")
    try:
        root.iconbitmap("")
    except Exception:
        pass

    IntroScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
