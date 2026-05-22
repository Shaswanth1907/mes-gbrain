from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base

# models
from app.models.machine import Machine
from app.models.issue import Issue
from app.models.document import Document, DocumentChunk
from app.models.maintenance import Maintenance
from app.models.production_kpi import ProductionKPI
from app.models.spare_part import SparePart
from app.models.technician import Technician
from app.models.work_order import WorkOrder
from app.models.approval import Approval
from app.models.monitoring_alert import MonitoringAlert
from app.models.feedback_learning import FeedbackLearning

# routers
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.machines import router as machines_router
from app.api.issues import router as issues_router
from app.api.maintenance import router as maintenance_router
from app.api.work_orders import router as work_orders_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.api.v1.test import router as test_router

app = FastAPI(
    title="MES GBrain API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(machines_router, prefix="/api/v1", tags=["Machines"])
app.include_router(issues_router, prefix="/api/v1", tags=["Issues"])
app.include_router(maintenance_router, prefix="/api/v1", tags=["Maintenance"])
app.include_router(work_orders_router, prefix="/api/v1", tags=["Work Orders"])
app.include_router(documents_router, prefix="/api/v1", tags=["Documents"])
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(test_router, prefix="/api/v1")
