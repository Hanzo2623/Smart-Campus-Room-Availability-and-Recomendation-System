# Smart Campus Room Availability & Recommendation System
**Course:** CC 102 – Advanced Computer Programming  
**School:** Batangas State University – CICS

---

## How to run

```
cd SmartCampus
python main.py
```

---

## File structure

```
SmartCampus/
│
├── main.py           ← Entry point – run this file
│
├── theme.py          ← All colours, fonts, and spacing constants
│
├── logic.py          ← Backend logic (rooms, scheduling, recommendations)
│
├── file_handler.py   ← File handling – reads/writes the two CSV logs
│
├── widgets.py        ← Reusable tkinter widget helpers
│
├── intro.py          ← Welcome / login screen (IntroScreen class)
│
├── app.py            ← Main application window and all pages
│
├── users_log.csv          ← Auto-created on first login
└── reservations_log.csv   ← Auto-created on first reservation
```

---

## File handling

Two CSV files are maintained automatically – no setup needed.

| File | What is recorded |
|---|---|
| `users_log.csv` | Name, Role, Login Time – one row per login |
| `reservations_log.csv` | Name, Role, Room, Time Slot, Reserved At – one row per reservation |

As the **manager** you can view both logs inside the app using the **📁 Records** tab in the sidebar.  From there you can also clear either log with the trash button.

---

## Module responsibilities

| Module | Responsibility |
|---|---|
| `theme.py` | Single source of truth for all colours/fonts – change here, updates everywhere |
| `logic.py` | Pure data operations – no UI imports; easy to unit-test |
| `file_handler.py` | All file I/O isolated here – easy to swap to a database later |
| `widgets.py` | Reusable UI atoms – keeps `app.py` free of repeated styling code |
| `intro.py` | Login/welcome screen; calls `file_handler.log_user()` on entry |
| `app.py` | All pages; calls `file_handler.log_reservation()` on successful add |
| `main.py` | Bootstraps sample data and launches the window |
