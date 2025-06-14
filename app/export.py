import csv
import json
from app.models import PDArray, Level

def export_pd_array_to_csv(session, pd_array_id, filename):
    levels = session.query(Level).filter(Level.pd_array_id == pd_array_id).all()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Level Type', 'Value', 'Label', 'Notes'])  # removed 'Timeframe'
        for lvl in levels:
            writer.writerow([lvl.level_type, lvl.value, lvl.label, lvl.notes])

def export_pd_array_to_json(session, pd_array_id, filename):
    levels = session.query(Level).filter(Level.pd_array_id == pd_array_id).all()

    data = []
    for lvl in levels:
        data.append({
            'level_type': lvl.level_type,
            'value': lvl.value,
            'label': lvl.label,
            'notes': lvl.notes
        })

    with open(filename, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
