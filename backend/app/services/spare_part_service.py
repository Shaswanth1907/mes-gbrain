import logging

from app.repositories.spare_part_repository import SparePartRepository

logger = logging.getLogger("mes_gbrain")


class SparePartService:
    def __init__(self, db):
        self.repo = SparePartRepository(db)

    def check_stock(self, part_code):
        part = self.repo.get_by_code(part_code)

        if not part:
            return {
                "message": f"Part {part_code} not found"
            }

        return {
            "part_code": part.part_code,
            "part_name": part.part_name,
            "quantity": part.quantity,
            "reorder_level": part.reorder_level
        }

    def reserve_stock(self, part_code, quantity):
        part = self.repo.get_by_code(part_code)

        if not part:
            return {
                "message": f"Part {part_code} not found"
            }

        if part.quantity < quantity:
            return {
                "message": "Insufficient stock",
                "available": part.quantity
            }

        part.quantity -= quantity
        self.repo.update(part)

        return {
            "message": "Stock reserved successfully",
            "part_code": part.part_code,
            "reserved_quantity": quantity,
            "remaining_stock": part.quantity
        }

    def low_stock(self):
        items = self.repo.get_low_stock()

        return {
            "low_stock_parts": [
                {
                    "part_code": p.part_code,
                    "part_name": p.part_name,
                    "quantity": p.quantity
                }
                for p in items
            ]
        }
