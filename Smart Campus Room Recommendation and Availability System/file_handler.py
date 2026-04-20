# ============================================================
# file_handler.py  –  File handling for users & reservations
# Smart Campus Room Availability and Recommendation System
# ============================================================
#
# Two CSV files are maintained automatically:
#   users_log.csv        – every login (name, role, timestamp)
#   reservations_log.csv – every successful room reservation
#
# The manager can open these files in any spreadsheet app or
# read them straight from the Records tab inside the system.
# ============================================================

import csv
import os
from datetime import datetime

# ── File paths (sit beside the running script) ──────────────
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
USERS_FILE       = os.path.join(BASE_DIR, "users_log.csv")
RESERVATIONS_FILE = os.path.join(BASE_DIR, "reservations_log.csv")

# ── Column headers ───────────────────────────────────────────
USER_HEADERS        = ["Name", "Role", "Login Time"]
RESERVATION_HEADERS = ["Name", "Role", "Room", "Time Slot", "Reserved At"]


# ────────────────────────────────────────────────────────────
# Internal helper
# ────────────────────────────────────────────────────────────

def _ensure_file(filepath: str, headers: list) -> None:
    """Create the CSV with headers if it doesn't exist yet."""
    if not os.path.exists(filepath):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


# ────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────

def log_user(name: str, role: str) -> None:
    """
    Append one row to users_log.csv when a user enters the system.
    Called from IntroScreen.enter_system().
    """
    _ensure_file(USERS_FILE, USER_HEADERS)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(USERS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([name, role, timestamp])


def log_reservation(name: str, role: str, room: str, time_slot: str) -> None:
    """
    Append one row to reservations_log.csv when a room schedule is
    successfully added.  Called from logic.add_schedule() via the UI.
    """
    _ensure_file(RESERVATIONS_FILE, RESERVATION_HEADERS)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RESERVATIONS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([name, role, room, time_slot, timestamp])


def read_users() -> list:
    """
    Return all rows from users_log.csv as a list of dicts.
    Returns [] if the file does not exist yet.
    """
    _ensure_file(USERS_FILE, USER_HEADERS)
    with open(USERS_FILE, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_reservations() -> list:
    """
    Return all rows from reservations_log.csv as a list of dicts.
    Returns [] if the file does not exist yet.
    """
    _ensure_file(RESERVATIONS_FILE, RESERVATION_HEADERS)
    with open(RESERVATIONS_FILE, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clear_users() -> None:
    """Wipe users_log.csv (keeps header row). Manager use only."""
    with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(USER_HEADERS)


def clear_reservations() -> None:
    """Wipe reservations_log.csv (keeps header row). Manager use only."""
    with open(RESERVATIONS_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(RESERVATION_HEADERS)
