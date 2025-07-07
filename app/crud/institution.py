from sqlalchemy.orm import Session

from app.models import Institution
from app.schemas.institution import InstitutionCreate, InstitutionUpdate


def create_institution(db: Session, institution: InstitutionCreate):
    db_institution = Institution(**institution.model_dump())
    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)
    return db_institution

def get_institutions_by_user(db: Session, user_id: str):
    return db.query(Institution).filter(Institution.user_id == user_id).all()

def get_institution(db: Session, institution_id:str):
    return db.query(Institution).filter(Institution.institution_id == institution_id).first()

def update_institution(db: Session, institution_id: str, updates: InstitutionUpdate):
    institution = db.query(Institution).filter(Institution.institution_id == institution_id).first()
    if not institution:
        return None
    for key, value in updates.model_dump(exclude_unset=True):
        setattr(institution, key, value)
    db.commit()
    db.refresh(institution)
    return institution

def delete_institution(db: Session, institution_id: str):
    institution = db.query(Institution).filter(Institution.institution_id == institution_id).first()
    if not institution:
        return None
    db.delete(institution)
    db.commit()
    return {"detail": f"Institution {institution_id} deleted."}
