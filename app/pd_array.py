from app.models import PDArray
from datetime import date

def add_pd_array(session, name, session_name, notes="", color=None):
    new_array = PDArray(name=name, session=session_name, notes=notes, color=color)
    session.add(new_array)
    session.commit()
    return new_array

def list_pd_arrays(session):
    return session.query(PDArray).order_by(PDArray.date.desc()).all()

def edit_pd_array(session, pd_array_id, name=None, session_name=None, notes=None):
    pd_array = session.query(PDArray).get(pd_array_id)
    if pd_array:
        if name: pd_array.name = name
        if session_name: pd_array.session = session_name
        if notes is not None: pd_array.notes = notes
        session.commit()
    return pd_array

def delete_pd_array(session, pd_array_id):
    pd_array = session.query(PDArray).get(pd_array_id)
    if pd_array:
        session.delete(pd_array)
        session.commit()
    return pd_array
