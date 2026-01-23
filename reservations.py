import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional

from tinydb import TinyDB, Query
from serializer import serializer


def _db_path(filename: str = "database.json") -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


@dataclass
class Reservation:
    reservation_id: str
    device_name: str
    user_id: str
    start: datetime
    end: datetime
    note: str = ""


class ReservationManager:
    def __init__(self) -> None:
        self._db = TinyDB(_db_path("database.json"), storage=serializer)
        self._table = self._db.table("reservations")

    @staticmethod
    def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
        # Überlappung, falls nicht (a endet vor b startet) und nicht (b endet vor a startet)
        return not (a_end <= b_start or b_end <= a_start)

    def is_available(self, device_name: str, start: datetime, end: datetime) -> bool:
        if end <= start:
            return False

        q = Query()
        existing = self._table.search(q.device_name == device_name)
        for r in existing:
            r_start = r["start"]
            r_end = r["end"]
            if self._overlaps(start, end, r_start, r_end):
                return False
        return True

    def create(self, res: Reservation) -> bool:
        # ID eindeutig?
        q = Query()
        if self._table.get(q.reservation_id == res.reservation_id) is not None:
            return False

        if not self.is_available(res.device_name, res.start, res.end):
            return False

        self._table.insert(asdict(res))
        return True

    def delete_by_id(self, reservation_id: str) -> bool:
        q = Query()
        existing = self._table.get(q.reservation_id == reservation_id)
        if existing is None:
            return False
        self._table.remove(doc_ids=[existing.doc_id])
        return True

    def find_all(self) -> List[Reservation]:
        return [
            Reservation(
                r["reservation_id"], r["device_name"], r["user_id"],
                r["start"], r["end"], r.get("note", "")
            )
            for r in self._table.all()
        ]

    def find_by_device(self, device_name: str) -> List[Reservation]:
        q = Query()
        res = self._table.search(q.device_name == device_name)
        return [
            Reservation(
                r["reservation_id"], r["device_name"], r["user_id"],
                r["start"], r["end"], r.get("note", "")
            )
            for r in res
        ]
