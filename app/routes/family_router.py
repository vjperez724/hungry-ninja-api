from fastapi import APIRouter, Depends, HTTPException

from app.auth import auth
from app.models import FamilyNewDTO
from app.services import FamilyServiceDep
from app.services.exceptions import DuplicateException

router = APIRouter(prefix="/families", dependencies=[Depends(auth.implicit_scheme)], tags=["families"])

@router.post("/")
async def create_family(family_new: FamilyNewDTO, family_service: FamilyServiceDep):
    try:
        result = await family_service.create_family(family_new)
        return result
    except DuplicateException as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.get("/self")
async def get_family_by_auth_id(family_service: FamilyServiceDep):
    result = await family_service.get_family_by_auth_id()
    if not result:
        raise HTTPException(status_code=404, detail="Family not found")
    return result