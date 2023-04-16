import os
import json

from pydantic import BaseModel
from typing import Dict, List, Optional
from quart import Quart, request, jsonify
from quart_schema import QuartSchema, validate_request, validate_response

from app import store
from app.learn import create_plan, fake_plan
from app.model import Plan

app = Quart(__name__)
QuartSchema(app)

DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def bad_request(message: str):
    return jsonify({"error": message}), 400


class CreatePlanRequest(BaseModel):
    goal: str
    model: Optional[str]
    openai_api_key: Optional[str]


class CreatePlanResponse(BaseModel):
    plan: Plan


@app.route("/v1/create_plan", methods=["POST"])
@validate_request(CreatePlanRequest)
@validate_response(CreatePlanResponse)
async def create_plan(data: CreatePlanRequest):
    plan = create_plan(
        goal=data.goal,
        model=data.model or DEFAULT_MODEL,
        openai_api_key=data.openai_api_key or DEFAULT_OPENAI_API_KEY,
        verbose=True,
    )
    return jsonify({"plan": json.loads(plan.json())})


class GetPlanRequest(BaseModel):
    id: str


class GetPlanResponse(BaseModel):
    plan: Plan


@app.route("/v1/get_plan", methods=["POST"])
@validate_request(GetPlanRequest)
@validate_response(GetPlanResponse)
async def get_plan(data: GetPlanRequest):
    # data = await request.json
    if data.id == "fake":
        return jsonify({"plan": json.loads(fake_plan().json())})
    plan = store.get_plan(data.id)
    return GetPlanResponse(plan=plan)
    # return jsonify({"plan": json.loads(plan.json())})


@app.after_request
def add_header(r):
    # for development
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
