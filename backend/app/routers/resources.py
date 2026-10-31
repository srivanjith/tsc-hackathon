from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Resource, Shelter
from ..schemas import ResourceResponse, ShelterResponse

router = APIRouter(prefix="/api", tags=["Resources & Shelters"])

@router.get("/resources", response_model=List[ResourceResponse])
def get_resources(db: Session = Depends(get_db)):
    return db.query(Resource).all()

@router.get("/shelters", response_model=List[ShelterResponse])
def get_shelters(db: Session = Depends(get_db)):
    return db.query(Shelter).all()
