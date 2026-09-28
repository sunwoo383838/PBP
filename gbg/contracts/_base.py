from pydantic import BaseModel, ConfigDict


class Contract(BaseModel):
    """모든 계약 모델의 기반: 선언하지 않은 필드는 거부한다."""
    model_config = ConfigDict(extra="forbid")
