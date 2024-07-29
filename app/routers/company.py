from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.models import Company, User
from app.schemas import CompanyCreate


router = APIRouter()

async def get_current_user(user_id: str):
    user_data = await db.users.find_one({"_id": ObjectId(user_id)})
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_mongo(user_data)

@router.post("/companies/", response_model=Company, status_code=201)
async def create_company(company: CompanyCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["super_admin", "company_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to add company")
    company_data = company.dict()
    new_company = await db.companies.insert_one(company_data)
    company_data["_id"] = str(new_company.inserted_id)
    return Company(**company_data)


@router.delete("/companies/{company_id}", status_code=204)
async def delete_company(company_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["super_admin", "company_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete company")
    try:
        company_object_id = ObjectId(company_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid company ID format")

    result = await db.companies.delete_one({"_id": company_object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"detail": "Company deleted"}
