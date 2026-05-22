import logging

from app.repositories.machine_repository import MachineRepository
from app.repositories.production_kpi_repository import ProductionKPIRepository

logger = logging.getLogger("mes_gbrain")


class ProductionKPIService:
    def __init__(self, db):
        self.machine_repo = MachineRepository(db)
        self.kpi_repo = ProductionKPIRepository(db)

    def get_machine_kpi(self, machine_code):
        try:
            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {"message": f"Machine {machine_code} not found"}

            rows = self.kpi_repo.get_by_machine_id(machine.id)

            if not rows:
                return {
                    "machine_code": machine_code,
                    "message": "No KPI data found"
                }

            planned = sum(r.planned_minutes or 0 for r in rows)
            runtime = sum(r.runtime_minutes or 0 for r in rows)
            downtime = sum(r.downtime_minutes or 0 for r in rows)

            total_count = sum(r.total_count or 0 for r in rows)
            good_count = sum(r.good_count or 0 for r in rows)
            reject_count = sum(r.reject_count or 0 for r in rows)

            ideal_cycle_time = rows[0].ideal_cycle_time or 1

            # DECIMAL calculations
            availability = (runtime / planned) if planned else 0
            quality = (good_count / total_count) if total_count else 0
            performance = ((ideal_cycle_time * total_count) / runtime) if runtime else 0

            # final OEE
            oee = availability * performance * quality

            return {
                "machine_code": machine_code,
                "planned_minutes": planned,
                "runtime_minutes": runtime,
                "downtime_minutes": downtime,

                "availability_percent": round(availability * 100, 2),
                "performance_percent": round(performance * 100, 2),

                "total_count": total_count,
                "good_count": good_count,
                "reject_count": reject_count,

                "quality_percent": round(quality * 100, 2),
                "ideal_cycle_time": ideal_cycle_time,

                "oee_percent": round(oee * 100, 2)
            }

        except Exception as e:
            import traceback
            print(traceback.format_exc())

            return {
                "message": str(e)
            }

    def create_kpi(
        self,
        machine_code,
        planned_minutes,
        runtime_minutes,
        downtime_minutes,
        total_count,
        good_count,
        reject_count
    ):
        machine = self.machine_repo.get_by_code(machine_code)

        if not machine:
            return {"message": f"Machine {machine_code} not found"}

        kpi = self.kpi_repo.create({
            "machine_id": machine.id,
            "planned_minutes": planned_minutes,
            "runtime_minutes": runtime_minutes,
            "downtime_minutes": downtime_minutes,
            "total_count": total_count,
            "good_count": good_count,
            "reject_count": reject_count
        })

        return {
            "message": "Production KPI created successfully",
            "machine_code": machine_code,
            "kpi_id": kpi.id
        }
