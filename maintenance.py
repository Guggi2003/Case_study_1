import os
from dataclasses import dataclass, asdict
from typing import Any, List

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage


def _db_path(filename: str = "database.json") -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


@dataclass
class Maintenance:
    maintenance_id: str
    device_name: str
    description: str
    cost: float = 0.0


class MaintenanceManager:
    def __init__(self) -> None:
        self._db = TinyDB(_db_path("database.json"), storage=JSONStorage)
        self._table = self._db.table("maintenances")

    def upsert(self, m: Maintenance) -> None:
        q = Query()
        existing = self._table.get(q.maintenance_id == m.maintenance_id)
        if existing is None:
            self._table.insert(asdict(m))
        else:
            self._table.update(asdict(m), doc_ids=[existing.doc_id])

    def delete_by_id(self, maintenance_id: str) -> bool:
        q = Query()
        existing = self._table.get(q.maintenance_id == maintenance_id)
        if existing is None:
            return False
        self._table.remove(doc_ids=[existing.doc_id])
        return True

    def find_all(self) -> List[Maintenance]:
        return [
            Maintenance(
                r["maintenance_id"],
                r["device_name"],
                r["description"],
                float(r.get("cost", 0.0)),
            )
            for r in self._table.all()
        ]

    def find_by_attribute(self, attr: str, value: Any, num_to_return: int = 100) -> List[Maintenance]:
        q = Query()
        res = self._table.search(q[attr] == value)
        res = res[:num_to_return] if num_to_return else res
        return [
            Maintenance(
                r["maintenance_id"],
                r["device_name"],
                r["description"],
                float(r.get("cost", 0.0)),
            )
            for r in res
        ]
