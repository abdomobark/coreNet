from typing import Optional
from pydantic import BaseModel, field_validator

class DeviceCreate(BaseModel):
    hostname: str
    ip_address: str
    device_type: str
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    site_id: Optional[int] = None
    management_protocol: Optional[str] = None
    management_port: Optional[int] = None
    is_active: bool = True
    description: Optional[str] = None

class DeviceUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    site_id: Optional[int] = None
    management_protocol: Optional[str] = None
    management_port: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None

class DeviceRead(BaseModel):
    id: int
    hostname: str
    ip_address: str
    device_type: str
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    site_id: Optional[int] = None
    management_protocol: Optional[str] = None
    management_port: Optional[int] = None
    is_active: bool
    description: Optional[str] = None

    # The DB column is PostgreSQL INET, which SQLAlchemy returns as an
    # ipaddress.IPv4Address/IPv6Address object on read. Coerce it to str so the
    # response validates (otherwise every device read raises ResponseValidationError).
    @field_validator("ip_address", mode="before")
    @classmethod
    def _coerce_ip_address(cls, v):
        return str(v) if v is not None else v

    class Config:
        from_attributes = True
