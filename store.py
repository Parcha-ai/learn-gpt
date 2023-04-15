import os
import uuid
from typing import List

from pydantic import BaseModel, Field
from tinydb import TinyDB
from tinydb.table import Table, Document

from model import Plan


class _Table(Table):
    document_id_class = str

    def _get_next_id(self):
        return str(uuid.uuid4())


class _DB(TinyDB):
    table_class = _Table


DATA_DIR = "./local-data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
db = _DB(DATA_DIR + "/db.json")


def save_plan(plan: Plan):
    db.upsert(Document(plan.dict(), doc_id=plan.id))


def get_plan(id: str) -> Plan:
    return Plan(**db.get(doc_id=id))


def get_all_plans() -> List[Plan]:
    return [Plan(**doc) for doc in db.all()]
