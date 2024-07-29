from pydantic import BaseModel, EmailStr
from typing import List, Optional


class CompanyCreate(BaseModel):
    name: str


class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    role: str
    company_id: Optional[str]


class CompanyAdminCreate(BaseModel):
    name: str
    email: EmailStr
    role: str


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    role: str
    company_id: str


class EmployeeUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]


class ProjectCreate(BaseModel):
    title: str
    description: str
    company_id: str


class ProjectUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]


class CommentCreate(BaseModel):
    project_id: str
    employee_id: str
    content: str
