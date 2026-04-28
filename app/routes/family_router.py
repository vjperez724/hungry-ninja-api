from fastapi import APIRouter, Depends

from app.auth import auth
from app.models import FamilyNewDTO
from app.services import FamilyServiceDep

router = APIRouter(prefix="/families", dependencies=[Depends(auth.implicit_scheme)], tags=["families"])

@router.post("/")
async def create_family(family_new: FamilyNewDTO, family_service: FamilyServiceDep):
    result = await family_service.create_family(family_new)
    return result