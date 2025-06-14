# 🗒️ ICT_Notepad

A personal web app to log, manage, and review ICT-style PD Arrays & Levels for trading.  
All data is stored locally in a lightweight SQLite database. No cloud. Fast. Private. Yours.

---

## 🎯 Purpose

Track your daily, weekly, and monthly PD Arrays with custom levels (Price or Time), tags, sessions, and filters.  
Useful for traders following Smart Money Concepts (SMC) or ICT methodology.

---

## 🚀 Features

### 📁 PD Arrays
- ➕ Add new PD Arrays (with name, session, notes, tags, color, and timeframes)
- 📝 Edit or 🗑️ Delete existing PD Arrays
- 📄 View all PD Arrays (with Tag filters and color preview)
- 📑 Duplicate existing PD Arrays (future)
- **Assign custom timeframes to each PD Array**

### 🧱 Levels
- ➕ Add new levels (custom labels and types, supports bulk/comma entry)
- 📋 View all levels in a PD Array (grouped by label and time)
- 🧭 Search levels across all arrays
- 🛠️ Edit/🗑️ Delete levels directly
- 🛠️ Add levels by template (e.g., Fibonacci, POI, etc.)
- 🗑️ Delete levels by type (bulk delete, future)

### 🏷️ Tags
- 🛠️ Manage tag list (create/delete)
- ✏️ Add/remove tags on each PD Array
- 🧪 Filter PD Arrays by Tag

### 📦 Tools
- 📤 Export PD Arrays/data to CSV/JSON (or full backup)
- 📥 Import PD Arrays from CSV (optional)
- 📊 Statistics and Recent Activity views

---

## 📊 How it Works

- **Add PD Arrays** (with name, color, tags, session, and timeframes)
- **Define Levels** (custom labels, types; add or edit at any time)
- **Bulk manage values**: select a PD Array, input all level values, and save as a single timestamped entry
- **View Level Entries**: grouped summary—each session shows all levels in one row with a timestamp
- **Filter, search, and export your data anytime**

---

## 🛠️ Tech Stack

- [Python 3.10+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) for UI
- [SQLAlchemy](https://www.sqlalchemy.org/) for ORM
- [SQLite](https://www.sqlite.org/) for database (PostgreSQL possible)
- Modular codebase (all business logic in `app/` folder)

---

## 🗂️ Project Structure

```bashj
ICT\_Notepad/
├── app.py                  # Streamlit entrypoint
├── main.py                 # (optional) CLI
├── requirements.txt
├── README.md
├── instructions.md         # Features list & plan
├── db/
│   └── trading\_guide.db
├── backups/
│   └── ... (optional, ignored by git)
├── app/
│   ├── **init**.py
│   ├── models.py           # SQLAlchemy models (PDArray, Level, LevelEntry, Tag)
│   ├── db\_utils.py         # DB helpers
│   ├── pd\_array.py         # PD Array logic
│   ├── level.py            # Level/LevelEntry logic
│   ├── tag.py              # Tags logic
│   ├── import\_utils.py     # CSV import logic
│   ├── export.py           # CSV/JSON export
│   ├── stats.py            # Statistics and activity logic
│   └── ...

```

---

## 🚀 Quick Start

---

> **Note:**  
> The database (`db/trading_guide.db`) and `backups/` folder are created automatically when you first run the app—no manual setup needed!

---

**Quick Start**

1. **Clone the repo:**
    ```bash
    git clone https://github.com/kopethan/ICT_Notepad.git
    cd ICT_Notepad
    ```

2. **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Initialize the database:**  
   *(This is automatic! When you run the app, `db/trading_guide.db` and the `backups/` folder will be created if they don’t exist.)*
    ```bash
    python init_db.py
    ```

4. **Run the app:**
    ```bash
    streamlit run app.py
    ```

---

## 🧩 Why is this different?

- All values are **logged historically**; nothing is overwritten
- Easy to retrieve, filter, and export years of trading levels
- **Local and private** by design (your data stays with you)
- Clean, intuitive UI, ready for extension

---

## 📝 License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

Kopethan Arudshelvan (and OpenAI ChatGPT)

---

## 🤝 Contribute / Support

- Open an issue or PR to help improve ICT_Notepad!
- Suggestions and feedback are always welcome.

---
