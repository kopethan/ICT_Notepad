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

import os
from app.models import Base
from app import engine
# test

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

# Clean, grouped menu
menu = st.sidebar.radio("📋 Menu", [
    "📁 PD Arrays",
    "➕ Add PD Array",
    "📝 Edit PD Array",
    "📄 View PD Arrays",
    "📑 Duplicate PD Array",
    "---",
    "🧱 Levels",
    "📋 View Levels",
    "📥 Bulk Manage Levels",
    "🧭 Search Levels",
    "🛠️ Edit Levels Template",
    "🗑️ Delete Levels Template",
    "---",
    "🏷️ Tags",
    "🛠️ Manage Tags",
    "✏️ Edit PD Array Tags",
    "---",
    "📦 Tools",
    "📤 Export PD Array",
    "📥 Import PD Array",
    "📊 Statistics",
    "🕒 Recent Activity"
])

# 1️⃣ Add PD Array (with Levels Template support)
if menu == "➕ Add PD Array":
    st.header("➕ Add New PD Array")
    name = st.text_input("Name")
    session_name = st.selectbox("Session", ["London", "NY", "Asia"])
    notes = st.text_area("Notes")
    color = st.color_picker("PD Array Color", "#33C1FF")
    tag_input = st.text_input("Tags (comma separated)", value="")
    timeframes_input = st.text_input("Timeframes (comma separated, e.g., 1m, 5m, 15m)", value="1h")

    add_levels_now = st.checkbox("Define Levels now for this PD Array?")
    if add_levels_now:
        levels_level_type = st.text_input("Levels' Level Type (ex: POI, Liquidity, FVG, etc.)")
        levels_labels_input = st.text_input("Levels Labels (comma separated, ex: High, Low, CE or 0.25, 0.5, 0.75, 1.0)")
        levels_timeframe = st.text_input("Levels' Timeframe", value="1h")

    if st.button("Add PD Array"):
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
                level_utils.add_level(session, new_array.id, levels_level_type, "", levels_timeframe, level_label, "")
            st.success(f"Added {len(levels_labels)} Levels to PD Array '{new_array.name}'.")

# 2️⃣ View PD Arrays
elif menu == "📄 View PD Arrays":
    st.header("📋 View PD Arrays")
    tags = tag_utils.list_tags(session)
    tag_options = ["All"] + [tag.name for tag in tags]
    selected_tag = st.selectbox("Filter by Tag", tag_options)
    if selected_tag == "All":
        pd_arrays = pd_array_utils.list_pd_arrays(session)
    else:
        pd_arrays = tag_utils.list_pd_arrays_by_tag(session, selected_tag)
    data = []
    for array in pd_arrays:
        color_bar = f"<span style='color:{array.color}'>▌</span>" if array.color else ""
        name_with_color = f"{color_bar} {array.name}"
        array_tags = ", ".join([tag.name for tag in array.tags])
        data.append([array.id, name_with_color, array.session, array.date, array.notes, array_tags])

    df = pd.DataFrame(data, columns=["ID", "Name", "Session", "Date", "Notes", "Tags"]) 
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
        new_name = st.text_input("PD Array Name", value=pd_array.name)
        new_session = st.selectbox("Session", ["London", "NY", "Asia"], index=["London", "NY", "Asia"].index(pd_array.session) if pd_array.session in ["London", "NY", "Asia"] else 0)
        new_notes = st.text_area("Notes", value=pd_array.notes)
        new_color = st.color_picker("PD Array Color", value=pd_array.color or "#33C1FF")
        new_timeframes = st.text_input("Timeframes (comma separated)", value=pd_array.timeframes or "")
        existing_tags = [tag.name for tag in pd_array.tags]
        all_tags = tag_utils.list_tags(session)
        all_tag_names = sorted([tag.name for tag in all_tags])
        selected_tags = st.multiselect("Tags", all_tag_names, default=existing_tags)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Changes"):
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
                st.success("PD Array updated!")
        with col2:
            confirm_delete = st.checkbox("Confirm deletion of this PD Array?")
            if st.button("Delete PD Array"):
                if confirm_delete:
                    session.delete(pd_array)
                    session.commit()
                    st.success("PD Array deleted!")
                else:
                    st.warning("Please check the confirmation box to delete the PD Array.")
    else:
        st.warning("No PD Arrays found.")

# 4️⃣ Duplicate PD Array
elif menu == "📑 Duplicate PD Array":
    st.header("📑 Duplicate PD Array")
    pd_arrays = pd_array_utils.list_pd_arrays(session)
    array_options = {f"{array.id} - {array.name} ({array.date})": array.id for array in pd_arrays}
    if array_options:
        selected_array = st.selectbox("Select PD Array to duplicate", list(array_options.keys()))
        pd_array_id = array_options[selected_array]
        new_name = st.text_input("New PD Array Name")
        new_session = st.selectbox("Session", ["London", "NY", "Asia"])
        new_notes = st.text_area("Notes for duplicate", value="")
        new_color = st.color_picker("Color for duplicate", value="#33C1FF")
        if st.button("Duplicate"):
            original = session.query(pd_array_utils.PDArray).get(pd_array_id)
            duplicate = pd_array_utils.add_pd_array(session, new_name, new_session, new_notes, new_color)
            for tag in original.tags:
                duplicate.tags.append(tag)
            for lvl in original.levels:
                level_utils.add_level(
                    session,
                    duplicate.id,
                    lvl.level_type,
                    lvl.value,
                    lvl.timeframe,
                    lvl.label,
                    lvl.notes
                )
            session.commit()
            st.success(f"✅ PD Array '{new_name}' duplicated with {len(original.levels)} levels.")
    else:
        st.warning("No PD Arrays available to duplicate.")

# 5️⃣ View Levels (Grouped Summary View Only)
elif menu == "📋 View Levels":
    st.header("📋 View Levels")

    # --- FILTERS ---
    all_levels = session.query(level_utils.Level).all()
    level_types_all = sorted(set([lvl.level_type for lvl in all_levels if lvl.level_type]))
    timeframes_all = sorted(set([lvl.timeframe for lvl in all_levels if lvl.timeframe]))

    selected_level_type = st.selectbox("Filter Level Type", ["All"] + level_types_all)
    selected_timeframe = st.selectbox("Filter Timeframe", ["All"] + timeframes_all)

    pd_arrays = pd_array_utils.list_pd_arrays(session)

    for pd_array in pd_arrays:
        levels = level_utils.list_levels(session, pd_array.id)
        # Apply filters
        levels = [
            lvl for lvl in levels
            if (selected_level_type == "All" or lvl.level_type == selected_level_type)
            and (selected_timeframe == "All" or lvl.timeframe == selected_timeframe)
        ]
        if not levels:
            continue

        # Get all entries for all levels in this PD Array
        label_list = [lvl.label for lvl in levels]
        all_entries = []
        for lvl in levels:
            for entry in lvl.entries:
                all_entries.append({
                    "timestamp": entry.timestamp,
                    "label": lvl.label,
                    "value": entry.value
                })

        # Group entries by timestamp
        grouped = defaultdict(dict)
        for e in all_entries:
            # Use only date+time to seconds for grouping (so identical timestamps are grouped)
            ts_key = e["timestamp"].replace(microsecond=0)
            grouped[ts_key][e["label"]] = e["value"]

        # Sort sessions by latest first
        session_groups = sorted(grouped.items(), key=lambda x: x[0], reverse=True)

        # Display each group (session/row)
        color = pd_array.color if pd_array.color else "#666"
        pd_name = html.escape(pd_array.name)
        pd_date = pd_array.date if pd_array.date else ""
        session_tag_html = f"{pd_name} ({pd_date})"

        for ts, values in session_groups:
            summary_line = " • ".join([
                f"{label} ({values.get(label, '-')})" for label in label_list
            ])
            st.markdown(
                f"""
                <div style='border-left: 6px solid {color}; padding: 0.75em 1em; margin-bottom: 0.5em; background-color: rgba(255,255,255,0.02); border-radius: 6px;'>
                    <details>
                        <summary style='font-weight: 600; font-size: 15px; cursor: pointer;'>
                            🕒 {ts.strftime('%Y-%m-%d %H:%M:%S')} — {session_tag_html} → {summary_line}
                        </summary>
                        <div style='margin-top: 8px;'>
                            <p><strong>Session:</strong> {pd_array.session}</p>
                            <p><strong>Tags:</strong> {', '.join([tag.name for tag in pd_array.tags])}</p>
                            {"<p><strong>Notes:</strong> " + html.escape(pd_array.notes) + "</p>" if pd_array.notes else ""}
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

        st.markdown(f"**Session:** {pd_array.session}")
        st.markdown(f"**Level Type:** {', '.join(set([lvl.level_type for lvl in pd_array.levels]))}")

        # Parse and display available timeframes
        tf_list = [tf.strip() for tf in (pd_array.timeframes or "").split(",") if tf.strip()]
        selected_timeframe = st.selectbox("Select Timeframe for this entry", tf_list or ["1h"])

        levels = level_utils.list_levels_by_pd_array_id(session, pd_array_id)

        st.markdown("### Enter Values for Each Level Label")
        level_inputs = {}
        for lvl in levels:
            level_inputs[lvl.id] = st.text_input(f"{lvl.label}:", key=f"entry_{lvl.id}")

        note = st.text_area("Note (optional)", key="bulk_note")

        if st.button("➕ Save Level Entries"):
            for lvl in levels:
                value = level_inputs.get(lvl.id, "").strip()
                if value:
                    level_utils.add_level_entry(session, lvl.id, value, note)
                    if lvl.timeframe != selected_timeframe:
                        lvl.timeframe = selected_timeframe  # Update timeframe if changed
            session.commit()
            st.success("Level entries saved!")
    else:
        st.warning("No PD Arrays found. Please add one.")

# 6️⃣ Search Levels
elif menu == "🧭 Search Levels":
    st.header("🔎 Search Levels")
    query = st.text_input("Search query (Level Type / Label / Timeframe)")
    all_levels = search_utils.search_levels(session, query if query else "")
    level_types = sorted(list(set([lvl.level_type for lvl in all_levels if lvl.level_type])))
    timeframes = sorted(list(set([lvl.timeframe for lvl in all_levels if lvl.timeframe])))
    selected_level_type = st.selectbox("Filter Level Type", ["All"] + level_types)
    selected_timeframe = st.selectbox("Filter Timeframe", ["All"] + timeframes)
    if st.button("Search"):
        filtered_levels = []
        for lvl in all_levels:
            if (selected_level_type != "All" and lvl.level_type != selected_level_type):
                continue
            if (selected_timeframe != "All" and lvl.timeframe != selected_timeframe):
                continue
            filtered_levels.append(lvl)
        data = []
        for lvl in filtered_levels:
            data.append([lvl.id, lvl.level_type, lvl.value, lvl.timeframe, lvl.label, lvl.notes, lvl.pd_array_id])
        df = pd.DataFrame(data, columns=["ID", "Level Type", "Value", "Timeframe", "Label", "Notes", "PD Array ID"])
        st.dataframe(df)

# 7️⃣ Edit Levels Template
elif menu == "🛠️ Edit Levels Template":
    st.header("🛠️ Edit Levels Template")
    pd_arrays = pd_array_utils.list_pd_arrays(session)
    array_options = {f"{array.id} - {array.name} ({array.date})": array.id for array in pd_arrays}
    if array_options:
        selected_array = st.selectbox("Select PD Array", list(array_options.keys()))
        pd_array_id = array_options[selected_array]
        pd_array = session.query(pd_array_utils.PDArray).get(pd_array_id)
        # Parse timeframes stored in PD Array (comma-separated)
        tf_list = [tf.strip() for tf in (pd_array.timeframes or "").split(",") if tf.strip()]
        existing_levels = level_utils.list_levels(session, pd_array_id)
        existing_labels = [lvl.label for lvl in existing_levels]
        if existing_labels:
            st.markdown(f"**Existing Levels:** {', '.join(existing_labels)}")
        else:
            st.info("No Levels currently defined for this PD Array.")
        st.subheader("➕ Add new Levels Template")
        levels_level_type = st.text_input("Levels' Level Type (ex: POI, Liquidity, FVG, etc.)")
        levels_labels_input = st.text_input("Levels Labels (comma separated, ex: High, Low, CE or 0.25, 0.5, 0.75, 1.0)")
        levels_timeframe = st.text_input("Levels' Timeframe", value="1h")
        if st.button("Add Levels Template"):
            levels_labels = [label.strip() for label in levels_labels_input.split(",") if label.strip()]
            for level_label in levels_labels:
                level_utils.add_level(session, pd_array_id, levels_level_type, "", levels_timeframe, level_label, "")
            st.success(f"Added {len(levels_labels)} Levels to PD Array '{pd_array.name}'.")
    else:
        st.warning("No PD Arrays found.")

# 8️⃣ Delete Levels Template
elif menu == "🗑️ Delete Levels Template":
    st.header("🗑️ Delete Levels Template (by Level Type)")
    pd_arrays = pd_array_utils.list_pd_arrays(session)
    array_options = {f"{array.id} - {array.name} ({array.date})": array.id for array in pd_arrays}
    if array_options:
        selected_array = st.selectbox("Select PD Array", list(array_options.keys()))
        pd_array_id = array_options[selected_array]
        levels = level_utils.list_levels(session, pd_array_id)
        existing_level_types = sorted(list(set([lvl.level_type for lvl in levels if lvl.level_type])))
        if existing_level_types:
            selected_level_type = st.selectbox("Select Level Type to delete", existing_level_types)
            if st.button("Delete Levels of this Type"):
                count_deleted = level_utils.delete_levels_by_type(session, pd_array_id, selected_level_type)
                st.success(f"Deleted {count_deleted} Levels of type '{selected_level_type}' from PD Array.")
        else:
            st.info("No Levels in this PD Array.")
    else:
        st.warning("No PD Arrays found.")

# 9️⃣ Manage Tags
elif menu == "🛠️ Manage Tags":
    st.header("🏷️ Manage Tags")
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
            st.success("Tag deleted!")

# 🔟 Edit PD Array Tags
elif menu == "✏️ Edit PD Array Tags":
    st.header("✏️ Edit PD Array Tags")
    pd_arrays = pd_array_utils.list_pd_arrays(session)
    array_options = {f"{array.id} - {array.name} ({array.date})": array.id for array in pd_arrays}
    if array_options:
        selected_array = st.selectbox("Select PD Array", list(array_options.keys()))
        pd_array_id = array_options[selected_array]
        pd_array = session.query(pd_array_utils.PDArray).get(pd_array_id)
        existing_tags = [tag.name for tag in pd_array.tags]
        all_tags = tag_utils.list_tags(session)
        all_tag_names = sorted([tag.name for tag in all_tags])
        selected_tags = st.multiselect("Select Tags", all_tag_names, default=existing_tags)
        if st.button("Update Tags"):
            pd_array.tags.clear()
            for tag_name in selected_tags:
                tag = tag_utils.get_or_create_tag(session, tag_name)
                pd_array.tags.append(tag)
            session.commit()
            st.success("Tags updated!")
    else:
        st.warning("No PD Arrays found.")

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

elif menu == "📥 Import PD Array":
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

elif menu == "📊 Statistics":
    st.header("📊 Statistics")
    stats = stats_utils.get_basic_statistics(session)
    st.metric("Total PD Arrays", stats["total_arrays"])
    st.metric("Total Levels", stats["total_levels"])
    data = []
    for timeframe, count in stats["timeframe_counts"]:
        data.append([timeframe, count])
    df = pd.DataFrame(data, columns=["Timeframe", "Count"])
    st.bar_chart(df.set_index("Timeframe"))

elif menu == "🕒 Recent Activity":
    st.header("🕒 Recent Activity (Last 10 Levels)")
    levels = stats_utils.get_recent_levels(session, limit=10)
    data = []
    for lvl in levels:
        data.append([lvl.id, lvl.level_type, lvl.value, lvl.timeframe, lvl.label, lvl.notes, lvl.pd_array_id])
    df = pd.DataFrame(data, columns=["ID", "Level Type", "Value", "Timeframe", "Label", "Notes", "PD Array ID"])
    st.dataframe(df)

elif menu == "📦 Tools":
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
