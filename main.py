# main.py

from app.db_utils import init_db, get_session
from app.models import PDArray, Level
from datetime import date
from sqlalchemy import func
import csv
import json
from app.backup import export_full_backup, import_full_backup

import os
from app.models import Base
from app import engine

# Ensure db folder exists
if not os.path.exists("db"):
    os.makedirs("db")
    print("📁 'db/' folder created.")

# Ensure database file exists
if not os.path.exists("db/trading_guide.db"):
    print("🛠️ Database not found. Creating...")
    Base.metadata.create_all(engine)
    print("✅ Database created.")

def add_pd_array(session):
    name = input("Enter PD Array name: ")
    session_name = input("Enter Session (London/NY/Asia): ")
    notes = input("Enter notes (optional): ")
    color = input("Enter color (hex, optional): ")
    timeframes = input("Enter timeframes (comma separated, e.g., 1m,5m,15m): ")

    new_array = PDArray(
        name=name,
        session=session_name,
        date=date.today(),
        notes=notes,
        color=color,
        timeframes=timeframes
    )

    session.add(new_array)
    session.commit()
    print(f"✅ PD Array '{name}' added.\n")

def list_pd_arrays(session):
    pd_arrays = session.query(PDArray).order_by(PDArray.date.desc()).all()
    print("\n📋 PD Arrays:")
    for array in pd_arrays:
        print(f"- {array.id}: {array.name} ({array.session}, {array.date})")
    print()

def add_level(session):
    list_pd_arrays(session)
    pd_array_id = int(input("Enter PD Array ID to add Levels to: "))
    pd_array = session.query(PDArray).get(pd_array_id)
    if not pd_array:
        print("❌ PD Array not found.\n")
        return

    level_type = input("Enter Level Type: ")
    value = input("Enter Value (price or time): ")
    timeframe = input("Enter Timeframe (1m/5m/1h/Daily/etc.): ")
    label = input("Enter Label: ")
    notes = input("Enter Notes (optional): ")

    new_level = Level(
        pd_array_id=pd_array_id,
        level_type=level_type,
        value=value,
        timeframe=timeframe,
        label=label,
        notes=notes
    )

    session.add(new_level)
    session.commit()
    print(f"✅ Level added to PD Array '{pd_array.name}'.\n")

def list_levels(session):
    list_pd_arrays(session)
    pd_array_id = int(input("Enter PD Array ID to view Levels: "))
    levels = session.query(Level).filter(Level.pd_array_id == pd_array_id).all()

    print(f"\n📋 Levels in PD Array {pd_array_id}:")
    for lvl in levels:
        print(f"- {lvl.id}: [{lvl.level_type}] {lvl.label} → {lvl.value} ({lvl.timeframe})")
    print()

def edit_pd_array(session):
    list_pd_arrays(session)
    pd_array_id = int(input("Enter PD Array ID to edit: "))
    pd_array = session.query(PDArray).get(pd_array_id)
    if not pd_array:
        print("❌ PD Array not found.\n")
        return

    pd_array.name = input(f"New name (current: {pd_array.name}): ") or pd_array.name
    pd_array.session = input(f"New session (current: {pd_array.session}): ") or pd_array.session
    pd_array.notes = input(f"New notes (current: {pd_array.notes}): ") or pd_array.notes
    pd_array.color = input(f"New color (current: {pd_array.color}): ") or pd_array.color
    pd_array.timeframes = input(f"New timeframes (current: {pd_array.timeframes}): ") or pd_array.timeframes

    session.commit()
    print("✅ PD Array updated.\n")

def edit_level(session):
    list_levels(session)
    level_id = int(input("Enter Level ID to edit: "))
    level = session.query(Level).get(level_id)
    if not level:
        print("❌ Level not found.\n")
        return

    level.level_type = input(f"New Level Type (current: {level.level_type}): ") or level.level_type
    level.value = input(f"New Value (current: {level.value}): ") or level.value
    level.timeframe = input(f"New Timeframe (current: {level.timeframe}): ") or level.timeframe
    level.label = input(f"New Label (current: {level.label}): ") or level.label
    level.notes = input(f"New Notes (current: {level.notes}): ") or level.notes

    session.commit()
    print("✅ Level updated.\n")

def delete_pd_array(session):
    list_pd_arrays(session)
    pd_array_id = int(input("Enter PD Array ID to delete: "))
    pd_array = session.query(PDArray).get(pd_array_id)
    if not pd_array:
        print("❌ PD Array not found.\n")
        return

    confirm = input(f"Are you sure you want to delete PD Array '{pd_array.name}' and all its Levels? (y/n): ")
    if confirm.lower() == 'y':
        session.delete(pd_array)
        session.commit()
        print("✅ PD Array deleted.\n")
    else:
        print("❌ Deletion canceled.\n")

def delete_level(session):
    list_levels(session)
    level_id = int(input("Enter Level ID to delete: "))
    level = session.query(Level).get(level_id)
    if not level:
        print("❌ Level not found.\n")
        return

    confirm = input(f"Are you sure you want to delete Level '{level.label}'? (y/n): ")
    if confirm.lower() == 'y':
        session.delete(level)
        session.commit()
        print("✅ Level deleted.\n")
    else:
        print("❌ Deletion canceled.\n")

def search_levels(session):
    query = input("Enter search term (Level Type / Label / Timeframe): ")

    levels = session.query(Level).filter(
        (Level.level_type.ilike(f'%{query}%')) |
        (Level.label.ilike(f'%{query}%')) |
        (Level.timeframe.ilike(f'%{query}%'))
    ).all()

    print(f"\n🔎 Found {len(levels)} Levels matching '{query}':")
    for lvl in levels:
        print(f"- {lvl.id}: [{lvl.level_type}] {lvl.label} → {lvl.value} ({lvl.timeframe}) [PD Array ID: {lvl.pd_array_id}]")
    print()

def export_pd_array(session):
    list_pd_arrays(session)
    pd_array_id = int(input("Enter PD Array ID to export: "))
    pd_array = session.query(PDArray).get(pd_array_id)
    if not pd_array:
        print("❌ PD Array not found.\n")
        return

    levels = session.query(Level).filter(Level.pd_array_id == pd_array_id).all()

    export_format = input("Choose export format (csv/json): ").lower()
    filename = f"pd_array_{pd_array_id}_{pd_array.name.replace(' ', '_')}.{export_format}"

    if export_format == 'csv':
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Level Type', 'Value', 'Timeframe', 'Label', 'Notes'])
            for lvl in levels:
                writer.writerow([lvl.level_type, lvl.value, lvl.timeframe, lvl.label, lvl.notes])
        print(f"✅ Exported to {filename}\n")

    elif export_format == 'json':
        data = []
        for lvl in levels:
            data.append({
                'level_type': lvl.level_type,
                'value': lvl.value,
                'timeframe': lvl.timeframe,
                'label': lvl.label,
                'notes': lvl.notes
            })
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        print(f"✅ Exported to {filename}\n")

    else:
        print("❌ Invalid export format.\n")

def import_pd_array(session):
    file_path = input("Enter CSV file path to import: ")
    pd_array_name = input("Enter name for the new PD Array: ")
    session_name = input("Enter Session (London/NY/Asia): ")
    notes = input("Enter notes (optional): ")
    color = input("Enter color (optional): ")
    timeframes = input("Enter timeframes (comma separated): ")

    new_array = PDArray(
        name=pd_array_name,
        session=session_name,
        date=date.today(),
        notes=notes,
        color=color,
        timeframes=timeframes
    )
    session.add(new_array)
    session.commit()

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_level = Level(
                    pd_array_id=new_array.id,
                    level_type=row['Level Type'],
                    value=row['Value'],
                    timeframe=row['Timeframe'],
                    label=row['Label'],
                    notes=row.get('Notes', '')
                )
                session.add(new_level)
            session.commit()
        print(f"✅ Imported Levels to PD Array '{pd_array_name}'.\n")
    except Exception as e:
        print(f"❌ Import failed: {e}\n")

def show_recent_activity(session, limit=10):
    levels = session.query(Level).order_by(Level.id.desc()).limit(limit).all()
    print(f"\n🕒 Last {limit} Levels added:")
    for lvl in levels:
        print(f"- {lvl.id}: [{lvl.level_type}] {lvl.label} → {lvl.value} ({lvl.timeframe}) [PD Array ID: {lvl.pd_array_id}]")
    print()

def show_statistics(session):
    total_arrays = session.query(PDArray).count()
    total_levels = session.query(Level).count()
    timeframe_counts = session.query(Level.timeframe, func.count(Level.id)).group_by(Level.timeframe).all()

    print("\n📊 Basic Statistics:")
    print(f"- Total PD Arrays: {total_arrays}")
    print(f"- Total Levels: {total_levels}")
    print("- Levels per Timeframe:")
    for timeframe, count in timeframe_counts:
        print(f"  {timeframe}: {count}")
    print()

def main():
    engine = init_db()
    session_obj = get_session(engine)

    while True:
        print("=== ICT Trading Guide CLI ===")
        print("1. Add PD Array")
        print("2. List PD Arrays")
        print("3. Add Level to PD Array")
        print("4. List Levels in PD Array")
        print("5. Edit PD Array")
        print("6. Edit Level")
        print("7. Delete PD Array (with Levels)")
        print("8. Delete Level")
        print("9. Search Levels")
        print("10. Export PD Array (CSV / JSON)")
        print("11. Import PD Array from CSV")
        print("12. Show Recent Activity")
        print("13. Show Basic Statistics")
        print("14. Backup All Data")
        print("15. Restore Backup from JSON")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            add_pd_array(session_obj)
        elif choice == '2':
            list_pd_arrays(session_obj)
        elif choice == '3':
            add_level(session_obj)
        elif choice == '4':
            list_levels(session_obj)
        elif choice == '5':
            edit_pd_array(session_obj)
        elif choice == '6':
            edit_level(session_obj)
        elif choice == '7':
            delete_pd_array(session_obj)
        elif choice == '8':
            delete_level(session_obj)
        elif choice == '9':
            search_levels(session_obj)
        elif choice == '10':
            export_pd_array(session_obj)
        elif choice == '11':
            import_pd_array(session_obj)
        elif choice == '12':
            show_recent_activity(session_obj)
        elif choice == '13':
            show_statistics(session_obj)
        elif choice == '14':
            filename = export_full_backup(session_obj)
            print(f"✅ Backup saved to: {filename}\n")
        elif choice == '15':
            path = input("Enter path to JSON backup file: ")
            import_full_backup(session_obj, path)
            print("✅ Backup restored.\n")
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.\n")

if __name__ == "__main__":
    main()
