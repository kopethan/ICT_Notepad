import json
import os
from datetime import datetime
from app.models import PDArray, Level, LevelEntry, Tag
from app.models import PDArray, Level, LevelEntry, Tag
from datetime import datetime

def export_full_backup(session, folder="backups"):
    os.makedirs(folder, exist_ok=True)
    data = {
        "pd_arrays": [],
        "tags": [],
    }

    tags = session.query(Tag).all()
    for tag in tags:
        data["tags"].append({"id": tag.id, "name": tag.name})

    arrays = session.query(PDArray).all()
    for array in arrays:
        array_data = {
            "name": array.name,
            "session": array.session,
            "notes": array.notes,
            "color": array.color,
            "timeframes": array.timeframes,
            "date": str(array.date) if array.date else None,
            "tags": [tag.name for tag in array.tags],
            "levels": []
        }
        for lvl in array.levels:
            lvl_data = {
                "label": lvl.label,
                "level_type": lvl.level_type,
                "value": lvl.value,
                "timeframe": lvl.timeframe,
                "notes": lvl.notes,
                "entries": [
                    {"value": e.value, "note": e.note, "timestamp": e.timestamp.isoformat()}
                    for e in lvl.entries
                ]
            }
            array_data["levels"].append(lvl_data)
        data["pd_arrays"].append(array_data)

    filename = os.path.join(folder, f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return filename

def import_full_backup(session, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    tag_map = {}
    for tag in data.get("tags", []):
        existing = session.query(Tag).filter_by(name=tag["name"]).first()
        if not existing:
            new_tag = Tag(name=tag["name"])
            session.add(new_tag)
            session.commit()
            tag_map[tag["name"]] = new_tag
        else:
            tag_map[tag["name"]] = existing

    for array_data in data.get("pd_arrays", []):
        pd_array = PDArray(
            name=array_data["name"],
            session=array_data["session"],
            notes=array_data["notes"],
            color=array_data["color"],
            timeframes=array_data["timeframes"],
            date=datetime.fromisoformat(array_data["date"]).date() if array_data.get("date") not in [None, "None", ""] else None,
        )
        session.add(pd_array)
        session.commit()

        for tag_name in array_data["tags"]:
            pd_array.tags.append(tag_map[tag_name])
        session.commit()

        for lvl_data in array_data["levels"]:
            lvl = Level(
                pd_array_id=pd_array.id,
                label=lvl_data["label"],
                level_type=lvl_data["level_type"],
                value=lvl_data["value"],
                timeframe=lvl_data["timeframe"],
                notes=lvl_data["notes"]
            )
            session.add(lvl)
            session.commit()

            for entry in lvl_data["entries"]:
                entry_obj = LevelEntry(
                    level_id=lvl.id,
                    value=entry["value"],
                    note=entry["note"],
                    timestamp=datetime.fromisoformat(entry["timestamp"])
                )
                session.add(entry_obj)
            session.commit()