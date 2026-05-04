from fastapi import HTTPException
from sqlmodel import select

from app.auth import AuthUserDep
from app.data import SessionDep, Family, FamilyMember
from app.models import FamilyNewDTO, FamilyDTO, FamilyMemberDTO
from app.services.exceptions import DuplicateException


class FamilyService:
    def __init__(self, session: SessionDep, user: AuthUserDep):
        self.session = session
        self.user = user

    async def create_family(self, new_family: FamilyNewDTO) -> FamilyDTO:
        # Check if user is already a member of a family
        existing_family = await self.get_family_by_auth_id()
        if existing_family:            
            raise DuplicateException("User is already a member of a family")

        # Create family
        family = Family(name=new_family.family_name, created_by=self.user.id)
        self.session.add(family)
        self.session.commit()
        self.session.refresh(family)

        # Create family member
        family_member = FamilyMember(
            name=new_family.member_name,
            auth_id=self.user.id,
            family_id=family.id,
            created_by=self.user.id,
        )
        self.session.add(family_member)
        self.session.commit()
        self.session.refresh(family_member)

        # Return family DTO with member
        return FamilyDTO(
            id=family.id,
            name=family.name,
            members=[FamilyMemberDTO(id=family_member.id, name=family_member.name)],
        )

    async def get_family_by_auth_id(self) -> FamilyDTO | None:
        family = self.session.exec(
            select(Family).join(FamilyMember).where(FamilyMember.auth_id == self.user.id)
        ).first()
        family_members = self.session.exec(
            select(FamilyMember).where(FamilyMember.family_id == family.id)
        ).all() if family else []
        family_member_dtos = [FamilyMemberDTO(id=member.id, name=member.name) for member in family_members]
        if family:
            return FamilyDTO(id=family.id, name=family.name, members=family_member_dtos)
        return None

