"""
Data models for printer operations
"""
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum


class PrinterStatus(Enum):
    """Printer status enumeration"""
    IDLE = "idle"
    PROCESSING = "processing"
    STOPPED = "stopped"
    UNKNOWN = "unknown"

    @classmethod
    def from_cups_state(cls, state: int) -> 'PrinterStatus':
        """Convert CUPS printer state to PrinterStatus enum"""
        state_map = {
            3: cls.IDLE,
            4: cls.PROCESSING,
            5: cls.STOPPED
        }
        return state_map.get(state, cls.UNKNOWN)

    @classmethod
    def from_string(cls, status_str: str) -> 'PrinterStatus':
        """Convert string status to PrinterStatus enum"""
        status_map = {
            'idle': cls.IDLE,
            'processing': cls.PROCESSING,
            'stopped': cls.STOPPED,
            'unknown': cls.UNKNOWN
        }
        return status_map.get(status_str.lower(), cls.UNKNOWN)


@dataclass
class Printer:
    """Printer information model"""
    index: int
    name: str
    status: PrinterStatus
    status_reasons: List[str]
    is_accepting: bool
    type: str
    is_default: bool
    location: str = ""
    model: str = ""
    uri: str = ""
    driver: str = ""
    port: str = ""
    job_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert PrinterStatus enum to string value
        if 'status' in data and isinstance(data['status'], PrinterStatus):
            data['status'] = data['status'].value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Printer':
        """Create from dictionary"""
        # Convert string status to PrinterStatus enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = PrinterStatus.from_string(data['status'])
        return cls(**data)


@dataclass
class APIResponse:
    """Unified API response model"""
    code: int
    msg: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def success(cls, data: Dict[str, Any] = None) -> 'APIResponse':
        """Create success response"""
        return cls(code=200, msg="success", data=data or {})

    @classmethod
    def error(cls, code: int, msg: str, data: Dict[str, Any] = None) -> 'APIResponse':
        """Create error response"""
        return cls(code=code, msg=msg, data=data or {})

    @classmethod
    def not_found(cls, msg: str = "Resource not found", data: Dict[str, Any] = None) -> 'APIResponse':
        """Create not found response"""
        return cls(code=404, msg=msg, data=data or {})

    @classmethod
    def server_error(cls, msg: str, data: Dict[str, Any] = None) -> 'APIResponse':
        """Create server error response"""
        return cls(code=500, msg=msg, data=data or {})


@dataclass
class PrintOptions:
    """Print options model"""
    copies: Optional[int] = None
    media: Optional[str] = None
    orientation: Optional[str] = None
    color_mode: Optional[str] = None
    quality: Optional[str] = None
    duplex: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrintOptions':
        """Create from dictionary"""
        return cls(**data)
