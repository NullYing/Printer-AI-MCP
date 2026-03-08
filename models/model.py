"""
Data models for printer operations
"""

from dataclasses import dataclass, asdict, fields
from typing import List, Optional, Dict, Any
from enum import Enum


class PrinterStatus(Enum):
    """Printer status enumeration"""

    IDLE = "idle"
    PROCESSING = "processing"
    STOPPED = "stopped"
    UNKNOWN = "unknown"

    @classmethod
    def from_cups_state(cls, state: int) -> "PrinterStatus":
        """Convert CUPS printer state to PrinterStatus enum"""
        state_map = {3: cls.IDLE, 4: cls.PROCESSING, 5: cls.STOPPED}
        return state_map.get(state, cls.UNKNOWN)

    @classmethod
    def from_string(cls, status_str: str) -> "PrinterStatus":
        """Convert string status to PrinterStatus enum"""
        status_map = {
            "idle": cls.IDLE,
            "processing": cls.PROCESSING,
            "stopped": cls.STOPPED,
            "unknown": cls.UNKNOWN,
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
        if "status" in data and isinstance(data["status"], PrinterStatus):
            data["status"] = data["status"].value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Printer":
        """Create from dictionary"""
        # Convert string status to PrinterStatus enum
        if "status" in data and isinstance(data["status"], str):
            data["status"] = PrinterStatus.from_string(data["status"])
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
    def success(cls, data: Dict[str, Any] = None) -> "APIResponse":
        """Create success response"""
        return cls(code=200, msg="success", data=data or {})

    @classmethod
    def error(cls, code: int, msg: str, data: Dict[str, Any] = None) -> "APIResponse":
        """Create error response"""
        return cls(code=code, msg=msg, data=data or {})

    @classmethod
    def not_found(
        cls, msg: str = "Resource not found", data: Dict[str, Any] = None
    ) -> "APIResponse":
        """Create not found response"""
        return cls(code=404, msg=msg, data=data or {})

    @classmethod
    def server_error(cls, msg: str, data: Dict[str, Any] = None) -> "APIResponse":
        """Create server error response"""
        return cls(code=500, msg=msg, data=data or {})


@dataclass
class PrintJob:
    """Print job information model"""

    job_id: int
    printer_name: str
    job_name: str
    status: str
    priority: int = 0
    size: int = 0
    pages: int = 0
    user: str = ""
    submitted_time: int = 0
    total_pages: int = 0
    pages_printed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrintJob":
        """Create from dictionary"""
        return cls(**data)




@dataclass
class WindowsPrintOptions:
    """Windows-specific print options using dmXXX format"""

    # Device Mode parameters for Windows API
    dmOrientation: Optional[int] = None  # 1=Portrait, 2=Landscape
    dmCopies: Optional[int] = None  # Number of copies
    dmColor: Optional[int] = None  # 1=Monochrome, 2=Color
    dmPaperSize: Optional[int] = None  # Paper size constant
    dmDuplex: Optional[int] = None  # 1=Simplex, 2=Vertical, 3=Horizontal
    dmDefaultSource: Optional[int] = None  # Paper source/bin
    dmMediaType: Optional[int] = None  # Media type
    dmPaperLength: Optional[int] = None  # Custom paper length (0.1mm units)
    dmPaperWidth: Optional[int] = None  # Custom paper width (0.1mm units)
    dmPrintQuality: Optional[int] = None  # Print quality
    dmCollate: Optional[int] = None  # 1=Collate, 0=No collate

    # Extra options not defined above
    extra_options: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values and merging extra_options"""
        result = {k: v for k, v in asdict(self).items() if v is not None and k != "extra_options"}
        if self.extra_options:
            result.update(self.extra_options)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WindowsPrintOptions":
        """Create from dictionary, unknown keys are stored in extra_options"""
        known_fields = {f.name for f in fields(cls)} - {"extra_options"}
        known = {k: v for k, v in data.items() if k in known_fields}
        extra = {k: v for k, v in data.items() if k not in known_fields}
        return cls(**known, extra_options=extra if extra else None)




@dataclass
class LinuxPrintOptions:
    """Linux/CUPS-specific print options using IPP format"""

    # Standard CUPS/IPP options
    copies: Optional[str] = None  # Number of copies as string
    media: Optional[str] = None  # Paper size (e.g., "A4", "Letter")
    orientation_requested: Optional[str] = None  # "3"=Portrait, "4"=Landscape
    print_color_mode: Optional[str] = None  # "monochrome", "color"
    print_quality: Optional[str] = None  # "3"=Draft, "4"=Normal, "5"=High
    sides: Optional[str] = (
        None  # "one-sided", "two-sided-long-edge", "two-sided-short-edge"
    )
    page_ranges: Optional[str] = None  # "1-5,10-15"
    number_up: Optional[str] = None  # Pages per sheet
    fit_to_page: Optional[str] = None  # "true", "false"
    scaling: Optional[str] = None  # Scaling percentage
    media_source: Optional[str] = None  # Paper source/tray
    media_type: Optional[str] = None  # Media type
    resolution: Optional[str] = None  # Print resolution

    # Extra options not defined above
    extra_options: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values and merging extra_options"""
        result = {k: v for k, v in asdict(self).items() if v is not None and k != "extra_options"}
        if self.extra_options:
            result.update(self.extra_options)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LinuxPrintOptions":
        """Create from dictionary, unknown keys are stored in extra_options"""
        known_fields = {f.name for f in fields(cls)} - {"extra_options"}
        known = {k: v for k, v in data.items() if k in known_fields}
        extra = {k: v for k, v in data.items() if k not in known_fields}
        return cls(**known, extra_options=extra if extra else None)


