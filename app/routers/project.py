from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate, CommentCreate
from app.routers.consumer import notify_clients

router = APIRouter()

@router.post("/projects/", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate, employee_id: str):
    employee_data = await db.users.find_one({"_id": ObjectId(employee_id)})
    if employee_data is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    if project.company_id != employee_data["company_id"]:
        raise HTTPException(status_code=403, detail="Employee does not belong to the specified company")

    project_data = project.dict()
    project_data["owner_id"] = employee_id
    new_project = await db.projects.insert_one(project_data)
    project_data["_id"] = str(new_project.inserted_id)

    return Project(**project_data)


@router.patch("/projects/{project_id}/", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    try:
        project_object_id = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project ID format")

    project_data = await db.projects.find_one({"_id": project_object_id})
    if project_data is None:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_update.dict(exclude_unset=True)
    await db.projects.update_one({"_id": project_object_id}, {"$set": update_data})
    
    updated_project = await db.projects.find_one({"_id": project_object_id})
    updated_project['_id'] = str(updated_project['_id'])
    return Project(**updated_project)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str):
    try:
        project_object_id = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project ID format")

    result = await db.projects.delete_one({"_id": project_object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return


@router.post("/projects/{project_id}/comments/", response_model=dict)
async def add_comment(project_id: str, comment: CommentCreate):
    try:
        project_object_id = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project ID format")

    comment_data = comment.dict()

    result = await db.projects.update_one(
        {"_id": project_object_id},
        {"$push": {"comments": comment_data}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Project not found or comment not added")

    await notify_clients(project_id, comment_data["content"])
    return {"detail": "Comment added"}
