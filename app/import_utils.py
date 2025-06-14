import csv
from app.models import PDArray, Level
from datetime import date

def import_pd_array_from_csv(session, file_path, name, session_name, notes="", color="#33C1FF", timeframes="1h"):
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

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            new_level = Level(
                pd_array_id=new_array.id,
                level_type=row['Level Type'],
                value=row['Value'],
                label=row['Label'],
                notes=row.get('Notes', '')
            )
            session.add(new_level)
        session.commit()

    return new_array
