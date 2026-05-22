from app.repositories.work_order_repository import WorkOrderRepository
from app.repositories.machine_repository import MachineRepository
from app.graph.graph_sync_service import graph_sync
import uuid
import logging

logger = logging.getLogger("mes_gbrain")


class WorkOrderService:
    def __init__(self, db):
        self.db = db
        self.work_order_repo = WorkOrderRepository(db)
        self.machine_repo = MachineRepository(db)

    def create_work_order(self, machine_code, description, priority="MEDIUM"):
        try:
            logger.info(f"Creating work order | machine_code={machine_code}")

            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            work_order = self.work_order_repo.create({
                "work_order_ref": f"WO-{str(uuid.uuid4())[:8]}",
                "machine_id": machine.id,
                "title": "AI Generated Work Order",
                "description": description,
                "priority": priority,
                "status": "OPEN",
                "assigned_to": "Ravi"
            })

            try:
                graph_sync.sync_work_order(work_order, machine.machine_code)
            except Exception as sync_error:
                logger.warning(f"Graph sync failed for work order: {str(sync_error)}")

            return {
                "message": "Work order created successfully",
                "work_order_id": work_order.id,
                "work_order_ref": work_order.work_order_ref,
                "machine_code": machine_code,
                "priority": work_order.priority
            }

        except Exception as e:
            logger.error(f"Create work order failed: {str(e)}")
            return {
                "message": "Failed to create work order"
            }

    def get_open_work_orders(self, machine_code):
        try:
            logger.info(f"Fetching open work orders | machine_code={machine_code}")

            machine = self.machine_repo.get_by_code(machine_code)

            if not machine:
                return {
                    "message": f"Machine {machine_code} not found"
                }

            work_orders = self.work_order_repo.get_open_by_machine_id(machine.id)

            return {
                "machine_code": machine_code,
                "open_work_orders": [
                    {
                        "work_order_ref": wo.work_order_ref,
                        "title": wo.title,
                        "priority": wo.priority,
                        "status": wo.status,
                        "assigned_to": wo.assigned_to
                    }
                    for wo in work_orders
                ]
            }

        except Exception as e:
            logger.error(f"Fetch work orders failed: {str(e)}")
            return {
                "message": "Failed to fetch work orders"
            }

    def close_work_order(self, work_order_ref):
        try:
            logger.info(f"Closing work order | ref={work_order_ref}")

            work_order = self.work_order_repo.close(work_order_ref)

            if not work_order:
                return {
                    "message": f"Work order {work_order_ref} not found"
                }

            return {
                "message": "Work order closed successfully",
                "work_order_ref": work_order.work_order_ref,
                "status": work_order.status
            }

        except Exception as e:
            logger.error(f"Close work order failed: {str(e)}")
            return {
                "message": "Failed to close work order"
            }

    def assign_work_order(self, work_order_ref, technician):
        try:
            work_order = self.work_order_repo.get_by_ref(work_order_ref)

            if not work_order:
                return {"message": "Work order not found"}

            work_order.assigned_to = technician
            self.db.commit()
            self.db.refresh(work_order)

            return {
                "message": "Work order assigned successfully",
                "work_order_ref": work_order_ref,
                "assigned_to": technician
            }

        except Exception as e:
            logger.error(str(e))
            return {"message": "Failed to assign work order"}
