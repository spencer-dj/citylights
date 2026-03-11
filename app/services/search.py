from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from app.database import get_db
from app.models import Quotes, Invoices

router = APIRouter()

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

@router.get("/search")
def global_search(search: str = Query(...), db: Session = Depends(get_db)):

    quotes = db.query(Quotes).filter(
        or_(
            Quotes.client_name.ilike(f"%{search}%"),
            cast(Quotes.id, String).ilike(f"%{search}%")
        )
    ).all()

    invoices = db.query(Invoices).filter(
        or_(
            Invoices.client_name.ilike(f"%{search}%"),
            cast(Invoices.id, String).ilike(f"%{search}%")
        )
    ).all()

    return {
        "quotes": [to_dict(q) for q in quotes],
        "invoices": [to_dict(i) for i in invoices]
    }