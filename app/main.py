from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.director import (
    create_plan,
    get_plan,
    approve_plan,
    reject_plan
)
from app.core.executor import execute_plan

app = FastAPI(
    title="BLAY AI",
    description="Multi-Agent AI Operating System",
    version="0.3.0"
)


class PlanRequest(BaseModel):
    prompt: str


@app.get("/")
def home():
    return {
        "name": "BLAY AI",
        "version": "0.3.0",
        "status": "online"
    }


@app.post("/plan")
def create_project_plan(request: PlanRequest):
    try:
        return create_plan(request.prompt)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/plan/{project_id}")
def read_project_plan(project_id: str):
    plan = get_plan(project_id)

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Project tidak ditemukan"
        )

    return plan


@app.post("/plan/{project_id}/approve")
def approve_project(project_id: str):
    try:
        return approve_plan(project_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/plan/{project_id}/reject")
def reject_project(project_id: str):
    try:
        return reject_plan(project_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.post("/plan/{project_id}/execute")
def execute_project(project_id: str):
    plan = get_plan(project_id)

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Project tidak ditemukan"
        )

    try:
        return execute_plan(plan)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
