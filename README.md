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
- 📄 View all PD Arrays (with tag filters and color preview)
- **Assign custom timeframes to each PD Array**

### 🧱 Levels
- ➕ Add levels (custom labels and types, bulk input supported)
- 📋 View all saved level entries (grouped by timestamp)
- 🧾 Edit saved level entries (all values in one session)
- 🛠️ Edit/🗑️ Delete individual levels
- 💾 Save bulk values for each PD Array session
- 🧹 Filter entries by level type, label, date, price, and timeframe (fully combined)

### 🏷️ Tags
- 🛠️ Manage tag list (create/delete)
- ✏️ Add/remove tags on each PD Array
- 🧪 Filter PD Arrays by tag

### 📦 Tools
- 📤 Export PD Arrays or full data to CSV/JSON
- 📥 Import PD Arrays from CSV (optional)
- 📊 View statistics and recent activity
- 🔄 Backup and restore full database

---

## 📊 How it Works

- **Create PD Arrays** with session, timeframes, tags, and custom level structure
- **Add and edit levels** freely, including reusable types (e.g. FVG, CE, etc.)
- **Store level values** daily by entering all values for an array at once (with timestamp)
- **View entries** in grouped format (1 row per session) with full filtering (date, price, type, label, tag)
- **Export or import data** as needed for analysis or archiving
- **Everything runs locally** — fast, private, and offline-ready

---

## 🛠️ Tech Stack

- [Python 3.10+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) for UI
- [SQLAlchemy](https://www.sqlalchemy.org/) for ORM
- [SQLite](https://www.sqlite.org/) for database (PostgreSQL possible)
- Modular codebase (all business logic in `app/` folder)

---

## 🗂️ Project Structure

```bash
ICT\_Notepad/
├── app.py                  # Streamlit entrypoint
├── main.py                 # (optional) CLI
├── requirements.txt
├── README.md
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

## 🚀 Quick Start

> 🆕 [Download latest release](https://github.com/kopethan/ICT_Notepad/releases)  
> ✅ Requires **Python 3.10+** (tested with Python 3.11) and **pip**

---

### 1. Clone the repository

```bash
git clone https://github.com/kopethan/ICT_Notepad.git
cd ICT_Notepad
```

---

### 2. (Recommended) Create a virtual environment

#### Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

> ✅ You should now see `(venv)` in your terminal

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Initialize the database (auto-created on first run)

```bash
python init_db.py
```

---

### 5. Run the app

```bash
streamlit run app.py
```

> 📂 Make sure you're in the `/ICT_Notepad/` directory before running.

---

### ❓ Troubleshooting

If you see this error:

```
error: externally-managed-environment
```

That means your system is protecting its Python install.
✅ Use the virtual environment method shown above, or:

```bash
pip install -r requirements.txt --break-system-packages
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


## ❤️ Support This Project

If you enjoy using **ICT_Notepad** and want to support its development, feel free to:

- ☕ [Buy me a coffee](https://coff.ee/kopy)

Your support helps keep this project free, open-source, and continuously improved.

