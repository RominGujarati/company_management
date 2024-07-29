from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.models import User
from app.schemas import AdminCreate, EmployeeCreate, CompanyAdminCreate, EmployeeUpdate

router = APIRouter()

async def get_current_user(user_id: str):
    user_data = await db.users.find_one({"_id": ObjectId(user_id)})
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_mongo(user_data)

@router.get('/start')
async def startup_event():
    existing_super_admin = await db.users.find_one({"role": "super_admin"})
    if not existing_super_admin:
        admin_data = AdminCreate(
            name="Admin User",
            email="admin@example.com",
            role="super_admin",
            company_id="None"
        )
        result = await db.users.insert_one(admin_data.dict())
        print(f"Super Admin created with ID: {result.inserted_id}")
        return {"message": "Startup event triggered"}   
    return {"message": "Startup event not  triggered"}



@router.post("/company_admin/", response_model=User, status_code=201)
async def create_user(user: CompanyAdminCreate, current_employee: User = Depends(get_current_user)):
    if current_employee.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not authorized to add company_admin")
    user_data = user.dict()
    user_data['company_id'] = "None"
    new_user = await db.users.insert_one(user_data)
    user_data["_id"] = str(new_user.inserted_id)
    return User(**user_data)


@router.post("/employee/", response_model=User, status_code=201)
async def create_employee(user: EmployeeCreate, current_employee: User = Depends(get_current_user)):
    if current_employee.role not in ["super_admin", "company_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to add employees")
    user_data = user.dict()
    new_user = await db.users.insert_one(user_data)
    user_data["_id"] = str(new_user.inserted_id)
    return User(**user_data)


@router.delete("/employees/{employee_id}", status_code=204)
async def delete_user(employee_id: str, current_employee: User = Depends(get_current_user)):
    if current_employee.role not in ["super_admin", "company_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to remove employees")
    try:
        user_object_id = ObjectId(employee_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = await db.users.delete_one({"_id": user_object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return


@router.patch("/employees/{employee_id}", response_model=User)
async def update_employee(employee_id: str, employee_update: EmployeeUpdate):
    try:
        employee_object_id = ObjectId(employee_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid employee ID format")

    employee_data = await db.users.find_one({"_id": employee_object_id})
    if employee_data is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if employee_data['role'] in ["super_admin", "company_admin"]:
        raise HTTPException(status_code=403, detail="Cannot update super_admin or company_admin")

    update_data = employee_update.dict(exclude_unset=True)
    await db.users.update_one({"_id": employee_object_id}, {"$set": update_data})
    
    updated_employee = await db.users.find_one({"_id": employee_object_id})
    updated_employee['_id'] = str(updated_employee['_id'])
    return User(**updated_employee)
