# 📈 ICT Trading Guide Tool

A personal web app to log, manage, and review ICT-style PD Arrays & Levels.  
All data is stored locally in a lightweight SQLite database. No cloud. Fast. Private. Yours.

---

## 🎯 Purpose

Track your daily, weekly, and monthly PD Arrays with custom levels (Price or Time), tags, sessions, and filters.  
Useful for traders following Smart Money Concepts (SMC) or ICT methodology.

---

## 🚀 Features

### 📁 PD Arrays
- ➕ Add new PD Arrays (with name, session, notes, tags)
- 📝 Edit or 🗑️ Delete existing PD Arrays
- 📄 View all PD Arrays (with Tag filters)
- 📑 Duplicate existing PD Arrays with all levels & tags

### 🧱 Levels
- ➕ Add new levels manually or via template
- 📋 View all levels in a PD Array
- 🧭 Search levels across all arrays
- 🛠️ Edit/🗑️ Delete levels directly (inline in View mode)
- 🛠️ Add levels by template (ex: Fibonacci, POI, etc.)
- 🗑️ Delete levels by type (bulk delete)

### 🏷️ Tags
- 🛠️ Manage tag list (create / delete)
- ✏️ Add/remove tags on each PD Array
- 🧪 Filter PD Arrays by Tag

### 📦 Tools
- 📤 Export PD Arrays to CSV/JSON
- 📥 Import PD Arrays from CSV
- 📊 Statistics (count, timeframe breakdown)
- 🕒 Recent Activity view (last 10 levels)

## Last updated

- **Create and organize PD Arrays** with custom colors, tags, and sessions
- **Define Levels** per PD Array (custom labels: High, Low, CE, etc.)
- **Bulk log values** for all levels (fast entry, per session/day)
- **Historical log:** every entry is timestamped and never overwritten
- **View Level Entries:** grouped by date/time, all labels on one line
- **Edit and duplicate PD Arrays**; manage tags and structure
- **Import/export data** (CSV/JSON) for backup or analysis
- **Filter/search** all your historical trading levels
- **Basic stats and recent activity overview**
- **Local-only:** all data stays on your device (uses SQLite)

---

## 🛠️ Tech Stack

- [Python 3.10+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) for UI
- [SQLAlchemy](https://www.sqlalchemy.org/) for ORM
- [SQLite](https://www.sqlite.org/) for database (PostgreSQL possible)
- Modular codebase (all business logic in `app/` folder)

---

## 🗂️ Project Structure

```
ict\_trading\_guide\_tool/
├── app.py                  # Streamlit entrypoint
├── main.py                 # (optional) CLI
├── requirements.txt
├── README.md
├── instructions.md         # Features list & plan
├── db/
│   └── trading\_guide.db
├── app/
│   ├── **init**.py
│   ├── models.py           # SQLAlchemy models (PDArray, Level, LevelEntry, Tag)
│   ├── db\_utils.py         # DB helpers
│   ├── pd\_array.py         # PD Array logic
│   ├── level.py            # Level/LevelEntry logic
│   ├── tag.py              # Tags logic
│   ├── import\_utils.py     # CSV import logic
│   ├── export.py           # CSV/JSON export
│   └── ...

```

---

## 🚀 Quick Start

1. **Clone the repo:**
    ```bash
    git clone https://github.com/kopethan/ict_trading_guide_tool.git
    cd ict_trading_guide_tool
    ```

2. **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Initialize the database:**
    ```bash
    python init_db.py
    ```

4. **Run the app:**
    ```bash
    streamlit run app.py
    ```

---

## 📊 How it Works

- **Add PD Arrays** (name, color, tags, session)
- **Define Levels** (custom labels, types)
- **Bulk manage values**: select PD Array, enter all level values, and save — a new session row is created
- **View levels:** Each entry session shows on its own line with timestamp and all values
- **Filter, search, and export your data anytime**

---

## 🧩 Why is this different?

- All values are **logged historically**; nothing is overwritten
- Easy to retrieve, filter, and export years of trading levels
- **Local and private** by design
- Clean, intuitive, and ready for future extension

---

## 📝 License

MIT License (or add your license here)

---

## 👤 Author

Kopethan Arudshelvan (and OpenAI ChatGPT)

---

## 🤝 Contribute / Support

- Open an issue or PR if you want to improve the tool!
- Suggestions and feedback are always welcome.

---
