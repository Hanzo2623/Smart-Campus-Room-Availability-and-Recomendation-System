# ============================================================
# logic.py  –  All backend / data logic (no UI code here)
# Smart Campus Room Availability and Recommendation System
# ============================================================

# ── Shared in-memory data store ──────────────────────────────
rooms: dict = {}
# Structure:
# { room_name: { "capacity": int, "features": [str], "schedules": [str] } }

# Current logged-in user (set by IntroScreen, used when logging reservations)
current_user: dict = {"name": "", "role": ""}


# ────────────────────────────────────────────────────────────
# Sample data
# ────────────────────────────────────────────────────────────

def initialize_sample_data() -> None:
    samples = {
        "Room 101":     {
            "capacity": 30,
            "features": ["projector", "whiteboard", "air conditioning"],
            "schedules": ["08:00-09:00", "10:00-11:00"],
        },
        "Room 202":     {
            "capacity": 50,
            "features": ["projector", "sound system", "air conditioning"],
            "schedules": ["09:00-10:00", "13:00-14:00"],
        },
        "Lab 301":      {
            "capacity": 40,
            "features": ["computers", "projector", "air conditioning"],
            "schedules": ["07:00-08:00", "11:00-12:00"],
        },
        "Conference A": {
            "capacity": 20,
            "features": ["whiteboard", "tv screen", "air conditioning"],
            "schedules": ["14:00-15:00"],
        },
        "Seminar Hall": {
            "capacity": 100,
            "features": ["projector", "sound system", "whiteboard", "air conditioning"],
            "schedules": ["15:00-17:00"],
        },
    }
    for name, data in samples.items():
        rooms[name] = data


# ────────────────────────────────────────────────────────────
# Time utilities
# ────────────────────────────────────────────────────────────

def parse_time(t: str):
    """Convert 'HH:MM' to total minutes.  Returns None on bad input."""
    parts = t.strip().split(":")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        return None


def validate_slot(slot: str):
    """
    Validate 'HH:MM-HH:MM'.
    Returns (True, (start_min, end_min)) or (False, error_message).
    """
    parts = slot.strip().split("-")
    if len(parts) != 2:
        return False, "Format must be HH:MM-HH:MM."
    s, e = parse_time(parts[0]), parse_time(parts[1])
    if s is None or e is None:
        return False, "Use 24-hour time: HH:MM-HH:MM."
    if s >= e:
        return False, "Start time must be before end time."
    return True, (s, e)


# ────────────────────────────────────────────────────────────
# Core operations
# ────────────────────────────────────────────────────────────

def detect_conflict(existing: list, new_slot: str) -> bool:
    """Return True if new_slot overlaps any slot in existing."""
    ok, res = validate_slot(new_slot)
    if not ok:
        return False
    ns, ne = res
    for slot in existing:
        ok2, ex = validate_slot(slot)
        if not ok2:
            continue
        es, ee = ex
        if ns < ee and ne > es:
            return True
    return False


def add_schedule(room_name: str, capacity, features_raw: str,
                 time_slot: str) -> tuple:
    """
    Add a time slot to a room (creating it if new).
    Returns (True, success_message) or (False, error_message).

    NOTE: the caller (UI) is responsible for calling
    file_handler.log_reservation() on success so that the
    currently logged-in user is captured there.
    """
    room_name = room_name.strip()
    time_slot = time_slot.strip()
    features  = [f.strip().lower() for f in features_raw.split(",") if f.strip()]

    if not room_name:
        return False, "Room name cannot be empty."
    try:
        cap = int(capacity)
        assert cap > 0
    except Exception:
        return False, "Capacity must be a positive whole number."

    ok, msg = validate_slot(time_slot)
    if not ok:
        return False, msg

    if room_name in rooms:
        if detect_conflict(rooms[room_name]["schedules"], time_slot):
            return False, (
                f"Conflict: '{time_slot}' overlaps an existing slot in '{room_name}'."
            )
        rooms[room_name]["schedules"].append(time_slot)
        rooms[room_name]["schedules"].sort()
    else:
        rooms[room_name] = {
            "capacity":  cap,
            "features":  features,
            "schedules": [time_slot],
        }

    return True, f"Schedule '{time_slot}' added to '{room_name}'."


def check_availability(room_name: str, time_slot: str) -> tuple:
    """Return (True/False, message)."""
    room_name = room_name.strip()
    time_slot = time_slot.strip()
    if not room_name or room_name not in rooms:
        return False, f"Room '{room_name}' not found."
    ok, msg = validate_slot(time_slot)
    if not ok:
        return False, msg
    if detect_conflict(rooms[room_name]["schedules"], time_slot):
        return False, f"'{room_name}' is OCCUPIED during {time_slot}."
    return True, f"'{room_name}' is AVAILABLE during {time_slot}."


def recommend_room(num_users, required_feature: str,
                   time_slot: str) -> tuple:
    """Return (best_room_name, message, candidates_list)."""
    time_slot        = time_slot.strip()
    required_feature = required_feature.strip().lower()

    try:
        users = int(num_users)
        assert users > 0
    except Exception:
        return None, "Number of users must be a positive integer.", []

    ok, msg = validate_slot(time_slot)
    if not ok:
        return None, msg, []

    candidates = []
    for name, data in rooms.items():
        if detect_conflict(data["schedules"], time_slot):
            continue
        if data["capacity"] < users:
            continue
        score = 15
        score -= min((data["capacity"] - users) // 10, 5)
        if required_feature and required_feature in data["features"]:
            score += 5
        candidates.append((name, score, data["capacity"], data["features"]))

    if not candidates:
        return None, "No suitable room found for the given requirements.", []

    candidates.sort(key=lambda x: x[1], reverse=True)
    best = candidates[0]
    return best[0], f"Best match: '{best[0]}' (Score: {best[1]})", candidates


def display_summary() -> list:
    """Return a list of room-info dicts for display."""
    return [
        {
            "name":      name,
            "capacity":  data["capacity"],
            "features":  ", ".join(data["features"]) or "None",
            "schedules": ", ".join(data["schedules"]) or "No schedules yet",
        }
        for name, data in rooms.items()
    ]
