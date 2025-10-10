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
class PrintOptions:
    """Base print options model"""

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
    def from_dict(cls, data: Dict[str, Any]) -> "PrintOptions":
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

    # Additional options for multipage support
    page_ranges: Optional[str] = None  # "1-5,10-15" for page selection
    number_up: Optional[int] = None  # Pages per sheet (1, 2, 4, 6, 8, 9, 16)
    scaling: Optional[int] = None  # Scaling percentage (50-200)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WindowsPrintOptions":
        """Create from dictionary"""
        return cls(**data)

    @classmethod
    def from_generic_options(cls, options: Dict[str, Any]) -> "WindowsPrintOptions":
        """Convert generic options to Windows dmXXX format"""
        dm_options = {}

        # Map generic options to dmXXX format
        if "copies" in options:
            dm_options["dmCopies"] = int(options["copies"])

        if "orientation" in options:
            orientation_map = {"portrait": 1, "landscape": 2}
            dm_options["dmOrientation"] = orientation_map.get(
                options["orientation"].lower(), 1
            )

        if "color_mode" in options:
            color_map = {"monochrome": 1, "color": 2, "black": 1}
            dm_options["dmColor"] = color_map.get(options["color_mode"].lower(), 1)

        if "duplex" in options:
            duplex_map = {
                "simplex": 1,
                "vertical": 2,
                "horizontal": 3,
                "off": 1,
                "long-edge": 2,
                "short-edge": 3,
            }
            dm_options["dmDuplex"] = duplex_map.get(options["duplex"].lower(), 1)

        if "paper_size" in options:
            # Common paper sizes (Windows constants)
            paper_map = {
                "a4": 9,
                "letter": 1,
                "legal": 5,
                "a3": 8,
                "a5": 11,
                "b4": 12,
                "b5": 13,
                "executive": 7,
                "folio": 14,
            }
            dm_options["dmPaperSize"] = paper_map.get(
                options["paper_size"].lower(), 9
            )  # Default to A4

        if "media_type" in options and isinstance(options["media_type"], int):
            dm_options["dmMediaType"] = options["media_type"]

        if "paper_source" in options and isinstance(options["paper_source"], int):
            dm_options["dmDefaultSource"] = options["paper_source"]

        if "print_quality" in options and isinstance(options["print_quality"], int):
            dm_options["dmPrintQuality"] = options["print_quality"]

        if "collate" in options:
            dm_options["dmCollate"] = 1 if options["collate"] else 0

        # Custom paper dimensions
        if "paper_width" in options:
            dm_options["dmPaperWidth"] = int(options["paper_width"])
        if "paper_length" in options:
            dm_options["dmPaperLength"] = int(options["paper_length"])

        # Multipage support options
        if "page_ranges" in options:
            dm_options["page_ranges"] = str(options["page_ranges"])
        return cls(**dm_options)


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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LinuxPrintOptions":
        """Create from dictionary"""
        return cls(**data)

    @classmethod
    def from_generic_options(cls, options: Dict[str, Any]) -> "LinuxPrintOptions":
        """Convert generic options to CUPS/IPP format"""
        cups_options = {}

        # Map generic options to CUPS format
        if "copies" in options:
            cups_options["copies"] = str(options["copies"])

        if "orientation" in options:
            orientation_map = {"portrait": "3", "landscape": "4"}
            cups_options["orientation_requested"] = orientation_map.get(
                options["orientation"].lower(), "3"
            )

        if "color_mode" in options:
            cups_options["print_color_mode"] = options["color_mode"].lower()

        if "duplex" in options:
            duplex_map = {
                "simplex": "one-sided",
                "off": "one-sided",
                "vertical": "two-sided-long-edge",
                "long-edge": "two-sided-long-edge",
                "horizontal": "two-sided-short-edge",
                "short-edge": "two-sided-short-edge",
            }
            cups_options["sides"] = duplex_map.get(
                options["duplex"].lower(), "one-sided"
            )

        if "media" in options:
            cups_options["media"] = options["media"]
        elif "paper_size" in options:
            cups_options["media"] = options["paper_size"]

        if "quality" in options:
            quality_map = {"draft": "3", "normal": "4", "high": "5"}
            cups_options["print_quality"] = quality_map.get(
                options["quality"].lower(), "4"
            )

        if "page_ranges" in options:
            cups_options["page_ranges"] = str(options["page_ranges"])

        if "pages_per_sheet" in options:
            cups_options["number_up"] = str(options["pages_per_sheet"])

        if "fit_to_page" in options:
            cups_options["fit_to_page"] = "true" if options["fit_to_page"] else "false"

        if "scaling" in options:
            cups_options["scaling"] = str(options["scaling"])

        if "media_source" in options:
            cups_options["media_source"] = options["media_source"]

        if "media_type" in options:
            cups_options["media_type"] = options["media_type"]

        if "resolution" in options:
            cups_options["resolution"] = str(options["resolution"])

        return cls(**cups_options)
