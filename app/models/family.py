from pydantic import BaseModel


class FamilyNewDTO(BaseModel):
    member_name: str
    family_name: str


class FamilyMemberDTO(BaseModel):
    id: int
    name: str


class FamilyDTO(BaseModel):
    id: int
    name: str
    members: list[FamilyMemberDTO] = []
