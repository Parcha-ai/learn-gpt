import uuid
from typing import List, Dict, Any

from pydantic import BaseModel, Field, validator


NAMESPACE_UUID = uuid.UUID(int=42)


class Resource(BaseModel):
    title: str
    description: str


class Exercise(BaseModel):
    description: str


class Subject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    description: str = ""
    reason: str = ""
    subjects: List["Subject"] = []
    resources: List[Resource] = []
    exercises: List[Exercise] = []


class Plan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    subject: Subject
