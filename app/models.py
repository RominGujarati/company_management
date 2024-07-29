from pydantic import BaseModel, EmailStr, Field, root_validator
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException

class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    employees: List[str] = []

    class Config:
        populate_by_name = True


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    email: EmailStr
    role: str
    company_id: Optional[str]

    class Config:
        populate_by_name = True

    @root_validator(pre=True)
    def check_role_and_company_id(cls, values):
        role = values.get('role')
        company_id = values.get('company_id')

        if role not in ['super_admin', 'company_admin', 'employee']:
            raise HTTPException(status_code=400, detail="Role must be 'company_admin' or 'employee'")

        if role == 'employee' and company_id is None:
            raise HTTPException(status_code=400, detail="employee must have a company_id")

        return values
    
    @classmethod
    def validate_unique_super_admin(cls, db):
        if cls.role == 'super_admin':
            existing_super_admin = db.users.find_one({"role": "super_admin"})
            if existing_super_admin:
                raise HTTPException(status_code=400, detail = "There can only be one super_admin")

    @classmethod
    def from_mongo(cls, data: dict):
        data['_id'] = str(data['_id'])
        return cls(**data)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    description: str
    company_id: str
    owner_id: str
    comments: List[dict] = []

    class Config:
        populate_by_name = True
