# app.py
import html
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import defaultdict
from app.models import Base
from app import db_utils
from app import pd_array as pd_array_utils
from app import level as level_utils
from app import search as search_utils
from app import export as export_utils
from app import import_utils as import_utils
from app import stats as stats_utils
import app.tag as tag_utils
import pandas as pd
from datetime import date
from app import backup as backup_utils
from app.models import Base
from app import engine
#from datetime import time

# Ensure 'db/' folder exists
if not os.path.exists("db"):
    os.makedirs("db")
    print("📁 'db/' folder created.")

# Ensure database file exists
if not os.path.exists("db/trading_guide.db"):
    print("🛠️ Database not found. Creating...")
    Base.metadata.create_all(engine)
    print("✅ Database created.")

# Ensure 'backups/' folder exists
if not os.path.exists("backups"):
    os.makedirs("backups")
    print("📁 'backups/' folder created.")

# DB setup
DB_PATH = 'db/trading_guide.db'
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
session = Session()

st.set_page_config(page_title="ICT Trading Guide", page_icon="📈", layout="wide")
st.title("📈 ICT Trading Guide Tool")

# ⬇️ Inject custom CSS
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.sidebar.title("📋 Navigation")
menu = st.sidebar.radio("Go to", [
    "★ PD Arrays",
    "➕ Add PD Array",
    "📄 View PD Arrays",
    "📝 Edit PD Array",

    "★ Levels",
    "📋 View Levels",
    "📥 Bulk Manage Levels",
    "🧾 Edit Level Entries",

    "★ Tags",
    "🏷️ Tags",

    "★ Tools",
    "📤 Export PD Array",
    "📥 Import PD Array",
    "📊 Statistics",
    "🕒 Recent Activity",
    "🔄 Backup / Restore"
])

# 1️⃣ Add PD Array (with Levels Template support)
if menu == "➕ Add PD Array":
    st.header("➕ Add New PD Array")
    name = st.text_input("Name")
    session_name = st.selectbox("Session", ["London", "NY", "Asia", "All", "Other"])
    notes = st.text_area("Notes")
    color = st.color_picker("PD Array Color", "#33C1FF")
    tag_input = st.text_input("Tags (comma separated)", value="")
    timeframes_input = st.text_input("Timeframes (comma separated, e.g., 1m, 5m, 15m)", value="1h")

    add_levels_now = st.checkbox("Define Levels now for this PD Array?")
    if add_levels_now:
        levels_level_type = st.text_input("Levels' Level Type (ex: POI, Liquidity, FVG, etc.)")
        levels_labels_input = st.text_input("Levels Labels (comma separated, ex: High, Low, CE or 0.25, 0.5, 0.75, 1.0)")

    if st.button("Add PD Array"):
        # ✅ Check if a PD Array with the same name already exists
        existing_array = session.query(pd_array_utils.PDArray).filter_by(name=name).first()
        if existing_array:
            st.warning(f"A PD Array with the name '{name}' already exists. Please choose a different name.")
        else:
            new_array = pd_array_utils.add_pd_array(session, name, session_name, notes, color, timeframes_input)
            tags_list = [tag.strip() for tag in tag_input.split(",") if tag.strip()]
            for tag_name in tags_list:
                tag = tag_utils.get_or_create_tag(session, tag_name)
                new_array.tags.append(tag)
            session.commit()
            st.success(f"PD Array '{new_array.name}' added with tags: {', '.join(tags_list)}")

            # Auto-create Levels if requested
            if add_levels_now:
                levels_labels = [label.strip() for label in levels_labels_input.split(",") if label.strip()]
                for level_label in levels_labels:
                                level_utils.add_level(session, new_array.id, levels_level_type, "", level_label, "")
                st.success(f"Added {len(levels_labels)} Levels to PD Array '{new_array.name}'.")

# 2️⃣ View PD Arrays
elif menu == "📄 View PD Arrays":
    st.header("📋 View PD Arrays")

    tags = tag_utils.list_tags(session)
    tag_options = ["All"] + [tag.name for tag in tags]
    selected_tag = st.selectbox("Filter by Tag", tag_options)

    # Fetch arrays
    if selected_tag == "All":
        pd_arrays = pd_array_utils.list_pd_arrays(session)
    else:
        pd_arrays = tag_utils.list_pd_arrays_by_tag(session, selected_tag)

    if not pd_arrays:
        st.info("No PD Arrays found.")
    else:
        table_rows = []
        for array in pd_arrays:
            color_icon = f"<span style='color:{array.color}'>▌</span>" if array.color else ""
            array_tags = ", ".join([tag.name for tag in array.tags])
            level_count = len(array.levels)

            table_rows.append([
                array.id,
                f"{color_icon} <strong>{array.name}</strong>",
                array.session,
                array.date.strftime("%Y-%m-%d") if array.date else "",
                f"{array.notes or ''}",
                array_tags,
                f"{level_count} level{'s' if level_count != 1 else ''}",
            ])

        df = pd.DataFrame(table_rows, columns=["ID", "Name", "Session", "Date", "Notes", "Tags", "Levels"])
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

# 3️⃣ Edit / Delete PD Array
elif menu == "📝 Edit PD Array":
    st.header("✏️ Edit / Delete PD Array")
    pd_arrays = pd_array_utils.list_pd_arrays(session)
    array_options = {f"{array.id} - {array.name} ({array.date})": array.id for array in pd_arrays}

    if array_options:
        selected_array = st.selectbox("Select PD Array to edit", list(array_options.keys()))
        pd_array_id = array_options[selected_array]
        pd_array = session.query(pd_array_utils.PDArray).get(pd_array_id)

        # 🧾 PD Array Info
        new_name = st.text_input("PD Array Name", value=pd_array.name)
        session_options = ["London", "NY", "Asia", "All", "Other"]
        new_session = st.selectbox("Session", session_options,
                                   index=session_options.index(pd_array.session) if pd_array.session in session_options else 0)
        new_notes = st.text_area("Notes", value=pd_array.notes)
        new_color = st.color_picker("PD Array Color", value=pd_array.color or "#33C1FF")
        new_timeframes = st.text_input("Timeframes (comma separated)", value=pd_array.timeframes or "")
        existing_tags = [tag.name for tag in pd_array.tags]
        all_tags = tag_utils.list_tags(session)
        all_tag_names = sorted([tag.name for tag in all_tags])
        selected_tags = st.multiselect("Tags", all_tag_names, default=existing_tags)

        # ----- Save / Delete buttons (just after PD Array info)
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.get("edit_success"):
                st.success("✅ PD Array info saved!")
                st.session_state["edit_success"] = False  # clear after showing once

            if st.button("💾 Save Changes"):
                pd_array.name = new_name
                pd_array.session = new_session
                pd_array.notes = new_notes
                pd_array.color = new_color
                pd_array.timeframes = new_timeframes
                pd_array.tags.clear()
                for tag_name in selected_tags:
                    tag = tag_utils.get_or_create_tag(session, tag_name)
                    pd_array.tags.append(tag)
                session.commit()

                st.session_state["edit_success"] = True  # ← set flag
                st.rerun()

        with col2:
            confirm_delete = st.checkbox("Confirm deletion of this PD Array?")
            if st.button("🗑️ Delete PD Array"):
                if confirm_delete:
                    session.delete(pd_array)
                    session.commit()
                    st.success("PD Array deleted.")
                else:
                    st.warning("Please check the confirmation box to delete the PD Array.")

        st.markdown("---")

        # ✏️ Unified Levels Editor
        st.markdown("### ✏️ Edit Existing Levels (Labels & Type)")
        existing_levels = level_utils.list_levels(session, pd_array_id)
        modified_levels = []

        if existing_levels:
            for lvl in existing_levels:
                col1, col2, col3 = st.columns([3, 3, 1])
                with col1:
                    label = st.text_input("Label", value=lvl.label, key=f"label_{lvl.id}")
                with col2:
                    ltype = st.text_input("Type", value=lvl.level_type, key=f"type_{lvl.id}")
                with col3:
                    if st.button("🗑️", key=f"delete_{lvl.id}"):
                        level_utils.delete_level(session, lvl.id)
                        st.warning(f"Deleted: {lvl.label}")
                        st.rerun()
                modified_levels.append((lvl.id, label, ltype))
            # Save any edits to existing levels
            if st.button("Save Level Edits"):
                for lvl_id, label, ltype in modified_levels:
                    level_utils.edit_level(session, lvl_id, label=label.strip(), level_type=ltype.strip())
                session.commit()
                st.success("✅ Level edits saved!")
                st.rerun()
        else:
            st.info("No levels defined for this PD Array yet.")

        # ➕ Add New Level(s)
        st.markdown("### ➕ Add New Level(s)")
        new_level_labels_input = st.text_input("New Labels (comma-separated)", key="new_labels")
        new_level_type_input = st.text_input("New Level Type", key="new_type")
        if st.button("Add New Level(s)"):
            labels = [lbl.strip() for lbl in new_level_labels_input.split(",") if lbl.strip()]
            ltype = new_level_type_input.strip()
            count = 0
            if labels and ltype:
                for label in labels:
                    level_utils.add_level(session, pd_array_id, ltype, "", label, "")
                    count += 1
            elif labels:
                for label in labels:
                    level_utils.add_level(session, pd_array_id, "", "", label, "")
                    count += 1
            elif ltype:
                level_utils.add_level(session, pd_array_id, ltype, "", "", "")
                count += 1
            if count > 0:
                st.success(f"✅ Added {count} new level(s).")
                session.commit()
                st.rerun()
            else:
                st.warning("Please enter at least a label or a type to add new level(s).")
    else:
        st.warning("No PD Arrays found.")

# 5️⃣ View Levels (Grouped by Timestamp, Across All PD Arrays)
elif menu == "📋 View Levels":
    st.header("📋 View Levels")

    import datetime, html
    from collections import defaultdict

    # ✅ Place these before the expander
    all_levels = session.query(level_utils.Level).all()
    pd_arrays_all = pd_array_utils.list_pd_arrays(session)
    level_types_all = sorted(set([lvl.level_type for lvl in all_levels if lvl.level_type]))
    labels_all = sorted(set([lvl.label for lvl in all_levels if lvl.label]))

    # ✅ Then only keep UI widgets inside the expander
    with st.expander("🔍 Show Filters", expanded=False):
        all_tags = set(tag.name for arr in pd_arrays_all for tag in arr.tags)
        selected_tags = st.multiselect("Tags (show PD Arrays with ANY of these tags)", sorted(all_tags))

        array_options = ["All"] + [arr.name for arr in pd_arrays_all]
        selected_array = st.selectbox("PD Array", array_options)
        selected_level_type = st.selectbox("Level Type", ["All"] + level_types_all)
        selected_label = st.selectbox("Label", ["All"] + labels_all)

        col1, col2 = st.columns(2)
        start_date = col1.date_input("Start Date", value=None)
        end_date = col2.date_input("End Date", value=None)

        col1, col2 = st.columns(2)
        price_min_input = col1.text_input("Min Price", "")
        price_max_input = col2.text_input("Max Price", "")

    price_min = price_max = None
    try:
        if price_min_input:
            price_min = float(price_min_input)
        if price_max_input:
            price_max = float(price_max_input)
    except Exception:
        st.warning("Invalid price input. Please enter valid numbers.")

    def pdarray_tag_match(arr):
        if not selected_tags:
            return True
        arr_tags = set(tag.name for tag in arr.tags)
        return bool(arr_tags & set(selected_tags))

    # Step 1: collect entries grouped by timestamp
    grouped_sessions = defaultdict(list)

    for pd_array in pd_arrays_all:
        if not pdarray_tag_match(pd_array):
            continue
        if selected_array != "All" and pd_array.name != selected_array:
            continue

        levels = level_utils.list_levels(session, pd_array.id)
        levels = [
            lvl for lvl in levels
            if (selected_level_type == "All" or lvl.level_type == selected_level_type) and
               (selected_label == "All" or lvl.label == selected_label)
        ]

        for lvl in levels:
            for entry in lvl.entries:
                ts = entry.timestamp.replace(microsecond=0)
                ts_date = ts.date()

                in_date = True
                if start_date and end_date:
                    in_date = (start_date <= ts_date <= end_date)
                elif start_date:
                    in_date = (ts_date >= start_date)
                elif end_date:
                    in_date = (ts_date <= end_date)

                in_price = True
                try:
                    v = float(entry.value)
                    if price_min is not None and price_max is not None:
                        in_price = (price_min <= v <= price_max)
                    elif price_min is not None:
                        in_price = (v >= price_min)
                    elif price_max is not None:
                        in_price = (v <= price_max)
                except Exception:
                    in_price = False if (price_min or price_max) else True

                if in_date and in_price:
                    grouped_sessions[ts].append({
                        "label": lvl.label,
                        "value": entry.value,
                        "note": entry.note,
                        "pd_name": pd_array.name,
                        "pd_color": pd_array.color or "#666",
                        "pd_session": pd_array.session,
                        "pd_date": pd_array.date,
                        "tags": [tag.name for tag in pd_array.tags],
                    })

    # Step 2: render grouped sessions
    for ts in sorted(grouped_sessions.keys(), reverse=True):
        entries = grouped_sessions[ts]
        pd_name = entries[0]["pd_name"]
        pd_date = entries[0]["pd_date"]
        pd_color = entries[0]["pd_color"]
        pd_session = entries[0]["pd_session"]
        tags = entries[0]["tags"]

        summary_line = " • ".join([f'{e["label"]} ({e["value"]})' for e in entries])
        notes = [e["note"] for e in entries if e["note"]]
        entry_note = notes[0] if notes else ""

        st.markdown(
            f"""
            <div style='border-left: 6px solid {pd_color}; padding: 0.75em 1em; margin-bottom: 0.5em; background-color: rgba(255,255,255,0.02); border-radius: 6px;'>
                <details>
                    <summary style='font-weight: 600; font-size: 15px; cursor: pointer;'>
                        {ts.strftime('%Y-%m-%d %H:%M:%S')} — {html.escape(pd_name)} ({pd_date or ""}) → {summary_line}
                    </summary>
                    <div style='margin-top: 8px;'>
                        <p><strong>Session:</strong> {pd_session}</p>
                        <p><strong>Tags:</strong> {', '.join(tags)}</p>
                        {"<p><strong>Entry Notes:</strong> " + html.escape(entry_note) + "</p>" if entry_note else ""}
                    </div>
                </details>
            </div>
            """,
            unsafe_allow_html=True
        )

# 📥 Bulk Manage Levels
elif menu == "📥 Bulk Manage Levels":
    st.header("📥 Bulk Manage Levels")

    pd_arrays = pd_array_utils.list_pd_arrays(session)
    array_options = {f"{array.id} - {array.name} ({array.date})": array.id for array in pd_arrays}

    if array_options:
        selected_array = st.selectbox("Select PD Array", list(array_options.keys()))
        pd_array_id = array_options[selected_array]
        pd_array = session.query(pd_array_utils.PDArray).get(pd_array_id)

        # --- Color bar preview here ---
        st.markdown(
            f"<span style='color:{pd_array.color}; font-size:30px;'>▌</span> "
            f"<span style='font-size:16px;'>{pd_array.name}</span>",
            unsafe_allow_html=True
        )

        st.markdown(f"**Session:** {pd_array.session}")
        st.markdown(f"**Level Type:** {', '.join(set([lvl.level_type for lvl in pd_array.levels]))}")

        # Parse and display available timeframes
        tf_list = [tf.strip() for tf in (pd_array.timeframes or "").split(",") if tf.strip()]
        selected_timeframe = st.selectbox("Select Timeframe for this entry", tf_list or ["1h"])

        levels = level_utils.list_levels_by_pd_array_id(session, pd_array_id)

        st.markdown("### Enter Values for Each Level Label")
        level_inputs = {}
        for lvl in levels:
            level_inputs[lvl.id] = st.text_input(f"**{lvl.label}**", key=f"entry_{lvl.id}")

        note = st.text_area("Note (optional)", key="bulk_note")

        if st.button("➕ Save Level Entries"):
            for lvl in levels:
                value = level_inputs.get(lvl.id, "").strip()
                if value:
                    level_utils.add_level_entry(session, lvl.id, value, note)
            session.commit()
            st.success("Level entries saved!")
    else:
        st.warning("No PD Arrays found. Please add one.")

# 8️⃣.2 Edit Level Entries
elif menu == "🧾 Edit Level Entries":
    st.header("🧾 Edit Level Entries (Grouped by Timestamp)")

    pd_arrays = pd_array_utils.list_pd_arrays(session)
    for pd_array in pd_arrays:
        levels = level_utils.list_levels(session, pd_array.id)
        all_entries = []
        for lvl in levels:
            for entry in lvl.entries:
                all_entries.append({
                    "timestamp": entry.timestamp.replace(microsecond=0),
                    "level_id": lvl.id,
                    "entry_id": entry.id,
                    "label": lvl.label,
                    "value": entry.value,
                    "note": entry.note,
                    "entry_obj": entry
                })

        from collections import defaultdict
        grouped_by_timestamp = defaultdict(list)
        for e in all_entries:
            grouped_by_timestamp[e["timestamp"]].append(e)

        for ts, entries in sorted(grouped_by_timestamp.items(), key=lambda x: x[0], reverse=True):
            with st.expander(f"🕒 {ts} — {pd_array.name} → {', '.join([f'{e['label']} ({e['value']})' for e in entries])}"):
                shared_note = entries[0]["note"]  # assume all entries in same group have same note

                # Editable values for each label
                updated_values = {}
                for e in entries:
                    updated_values[e["entry_id"]] = st.text_input(f"{e['label']}", value=e["value"], key=f"val_{e['entry_id']}")

                # Shared note (only one per group)
                new_note = st.text_area("Shared Note", value=shared_note, key=f"note_{ts}")

                # Save all
                if st.button("💾 Save All Changes", key=f"save_group_{ts}"):
                    for e in entries:
                        new_val = updated_values[e["entry_id"]]
                        e["entry_obj"].value = new_val
                        e["entry_obj"].note = new_note  # update same note for all
                    session.commit()
                    st.success("✅ Entries updated.")

                # Delete all
                if st.button("🗑️ Delete Entire Entry Group", key=f"delete_group_{ts}"):
                    for e in entries:
                        session.delete(e["entry_obj"])
                    session.commit()
                    st.warning("❌ Entire entry group deleted.")
                    st.rerun()
# 9️⃣ 🏷️ Tags
elif menu == "🏷️ Tags":
    st.header("🏷️ Manage Tags")

    # ➕ Add Tag Section
    with st.expander("➕ Add New Tag", expanded=True):
        new_tag_name = st.text_input("Tag Name", "")
        if st.button("Add Tag"):
            if not new_tag_name.strip():
                st.warning("Please enter a valid tag name.")
            else:
                existing = session.query(tag_utils.Tag).filter_by(name=new_tag_name.strip()).first()
                if existing:
                    st.warning("This tag already exists.")
                else:
                    tag_utils.get_or_create_tag(session, new_tag_name.strip())
                    session.commit()
                    st.success(f"✅ Tag '{new_tag_name}' added.")
                    st.rerun()

    # 📋 List Existing Tags
    tags = tag_utils.list_tags(session)
    if not tags:
        st.info("No Tags found.")
    else:
        data = []
        for tag in tags:
            data.append([tag.id, tag.name, len(tag.pd_arrays)])
        df = pd.DataFrame(data, columns=["ID", "Tag Name", "Linked PD Arrays"])
        st.dataframe(df)

        tag_options = {f"{tag.id} - {tag.name}": tag.id for tag in tags}
        selected_tag = st.selectbox("Select Tag to delete", list(tag_options.keys()))
        tag_id = tag_options[selected_tag]

        if st.button("Delete Tag"):
            tag_utils.delete_tag(session, tag_id)
            session.commit()
            st.success("Tag deleted!")
            st.rerun()

# 📦 Tools
elif menu == "📤 Export PD Array":
    st.header("📤 Export PD Array")
    pd_arrays = pd_array_utils.list_pd_arrays(session)
    array_options = {f"{array.id} - {array.name} ({array.date})": array.id for array in pd_arrays}
    if array_options:
        selected_array = st.selectbox("Select PD Array", list(array_options.keys()))
        pd_array_id = array_options[selected_array]
        export_format = st.selectbox("Format", ["CSV", "JSON"])
        filename = st.text_input("Filename (without extension)")
        if st.button("Export"):
            if export_format == "CSV":
                export_utils.export_pd_array_to_csv(session, pd_array_id, filename + ".csv")
                st.success(f"Exported to {filename}.csv")
            else:
                export_utils.export_pd_array_to_json(session, pd_array_id, filename + ".json")
                st.success(f"Exported to {filename}.json")
    else:
        st.warning("No PD Arrays found.")

# Import PD Array
elif menu == "📦 📥 Import PD Array":
    st.header("📥 Import PD Array from CSV")
    uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])
    name = st.text_input("New PD Array Name")
    session_name = st.selectbox("Session", ["London", "NY", "Asia"])
    notes = st.text_area("Notes")
    if uploaded_file and st.button("Import"):
        with open("temp_import.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        new_array = import_utils.import_pd_array_from_csv(session, "temp_import.csv", name, session_name, notes)
        st.success(f"PD Array '{new_array.name}' imported.")

# 9️⃣ Statistics
elif menu == "📊 Statistics":
    st.header("📊 Statistics Dashboard")
    stats = stats_utils.get_basic_statistics(session)

    # Key metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("PD Arrays", stats['total_pd_arrays'])
    col2.metric("Levels", stats['total_levels'])
    col3.metric("Level Entries", stats['total_entries'])

    # Levels per PD Array chart
    df_levels = pd.DataFrame(stats['levels_per_array'], columns=["PD Array", "Levels"])
    if not df_levels.empty:
        st.subheader("📊 Levels per PD Array")
        st.bar_chart(df_levels.set_index("PD Array"))

    # Most common Level Types
    df_types = pd.DataFrame(stats['level_type_counts'], columns=["Level Type", "Count"])
    if not df_types.empty:
        st.subheader("🏷️ Level Types Usage")
        st.bar_chart(df_types.set_index("Level Type"))

    # Recent Activity (last 5 Level Entries)
    from app.models import LevelEntry
    recent_entries = session.query(LevelEntry).order_by(LevelEntry.timestamp.desc()).limit(5).all()
    st.subheader("🕒 Recent Entries")
    for entry in recent_entries:
        st.markdown(f"- {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | Value: {entry.value} | Note: {entry.note or ''}")

# Recent Activity
elif menu == "🕒 Recent Activity":
    st.header("🕒 Recent Activity (Last 10 Levels)")
    levels = stats_utils.get_recent_levels(session, limit=10)
    data = []
    for lvl in levels:
        data.append([lvl.id, lvl.level_type, lvl.value, lvl.label, lvl.notes, lvl.pd_array_id])
    df = pd.DataFrame(data, columns=["ID", "Level Type", "Value", "Label", "Notes", "PD Array ID"])
    st.dataframe(df)

# 🔄 Backup / Restore
elif menu == "🔄 Backup / Restore":
    st.subheader("Backup / Restore")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📤 Backup All Data"):
            filename = backup_utils.export_full_backup(session)
            st.success(f"Backup saved as `{filename}`")

    with col2:
        uploaded_file = st.file_uploader("📥 Restore from JSON", type=["json"])
        if uploaded_file and st.button("Restore Backup"):
            with open("temp_restore.json", "wb") as f:
                f.write(uploaded_file.getbuffer())
            backup_utils.import_full_backup(session, "temp_restore.json")
            st.success("Backup restored into the database.")
