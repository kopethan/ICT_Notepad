from app.models import Tag

def get_or_create_tag(session, tag_name):
    tag = session.query(Tag).filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        session.add(tag)
        session.commit()
    return tag

def list_tags(session):
    return session.query(Tag).order_by(Tag.name).all()

def list_pd_arrays_by_tag(session, tag_name):
    tag = session.query(Tag).filter_by(name=tag_name).first()
    if tag:
        return tag.pd_arrays
    return []

def delete_tag(session, tag_id):
    tag = session.query(Tag).get(tag_id)
    if tag:
        # First, remove tag from all PD Arrays
        for pd_array in tag.pd_arrays:
            pd_array.tags.remove(tag)
        session.delete(tag)
        session.commit()
    return tag

def get_tag_by_name(session, tag_name):
    return session.query(Tag).filter_by(name=tag_name).first()
