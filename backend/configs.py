
from pydantic import BaseModel
from typing import Dict, List, Optional

# Model
class SupportedModels(Enum):
    CLAUDE_HAIKU = "arn:aws:bedrock:us-west-2:150965600522:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0"

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
