
from pydantic import BaseModel
from typing import Dict, List, Optional

# Pydantic models
class SensorReadings(BaseModel):
    PowerMotor: float
    CurrentMotor: float
    TempBrassBearingDE: float
    SpeedMotor: float
    SpeedRoller: float
    TempOilGear: float
    TempBearingMotorNDE: float
    TempWindingMotorPhase_U: float
    TempWindingMotorPhase_V: float
    TempWindingMotorPhase_W: float
    Vibration: Optional[float] = None


class MachineData(BaseModel):
    timestamp: str
    machine_type: str
    sensor_readings: SensorReadings

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = None

class ROIRequest(BaseModel):
    current_health_percentage: float
    comparison_health_percentage: float
    repair_cost: float
    daily_production_value: float
