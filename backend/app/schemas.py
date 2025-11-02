"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

# ===== Equipment Schemas =====

class EquipmentCreate(BaseModel):
    equipment_id: str = Field(..., max_length=20)
    equipment_type: str = Field(..., max_length=50)
    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year_manufactured: Optional[int] = None
    purchase_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=100)
    operating_hours: Optional[Decimal] = Field(default=0)
    last_service_date: Optional[date] = None

class EquipmentUpdate(BaseModel):
    equipment_type: Optional[str] = Field(None, max_length=50)
    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year_manufactured: Optional[int] = None
    purchase_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=100)
    operating_hours: Optional[Decimal] = None
    last_service_date: Optional[date] = None

# ===== Maintenance Record Schemas =====

class MaintenanceRecordCreate(BaseModel):
    equipment_id: str = Field(..., max_length=20)
    maintenance_date: date
    type_id: int = Field(..., ge=1, le=3)  # 1=Preventive, 2=Corrective, 3=Emergency
    description: Optional[str] = None
    technician: Optional[str] = Field(None, max_length=100)
    parts_replaced: Optional[str] = None
    total_cost: Optional[Decimal] = Field(default=0)
    downtime_hours: Optional[Decimal] = Field(default=0)

# ===== Failure Event Schemas =====

class FailureEventCreate(BaseModel):
    equipment_id: str = Field(..., max_length=20)
    failure_date: date
    failure_type: Optional[str] = Field(None, max_length=100)
    severity: str = Field(..., pattern="^(Minor|Moderate|Critical)$")
    description: Optional[str] = None
    repair_cost: Optional[Decimal] = Field(default=0)
    downtime_hours: Optional[Decimal] = Field(default=0)
    prevented_by_maintenance: bool = False

# ===== Schedule Schemas =====

class ScheduleUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(Scheduled|In Progress|Completed|Cancelled)$")
    assigned_technician: Optional[str] = Field(None, max_length=100)
    scheduled_date: Optional[date] = None
    notes: Optional[str] = None

class ScheduleComplete(BaseModel):
    actual_cost: Decimal
    actual_duration_hours: Decimal
    completion_notes: Optional[str] = None

# ===== Response Schemas =====

class MessageResponse(BaseModel):
    message: str
    success: bool = True

class EquipmentResponse(BaseModel):
    equipment_id: str
    equipment_type: str
    brand: Optional[str]
    model: Optional[str]
    location: Optional[str]
    operating_hours: Optional[Decimal]
