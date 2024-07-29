from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import db
from .routers import company, employee, project, consumer
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections = []
app.include_router(company.router, prefix="/api")
app.include_router(employee.router, prefix="/api")
app.include_router(project.router, prefix="/api")
app.include_router(consumer.router, prefix="/ws")

@app.on_event("shutdown")
async def shutdown_db_client():
    db.client.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
