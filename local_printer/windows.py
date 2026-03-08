"""
Windows Printer Operations Module
"""

import subprocess
import json
from typing import Dict, Any, List, Optional

import win32con
import win32gui
import win32print
import pywintypes
import win32ui
from utils.logger import logger
from models.model import (
    APIResponse,
    PrinterStatus,
    Printer,
    PrintJob,
    WindowsPrintOptions,
)
from typing import Optional


def print_file_prompt():
    return """
    Windows Printer Operations Module
    
    This module provides comprehensive printer management capabilities for Windows systems using the Windows Print API.
    
    Workflow:
    1. Get printer list - Retrieve all available printers with their status and capabilities
    2. Get printer status - Check if a specific printer is ready and accepting jobs
    3. Get printer attributes - Obtain detailed printer capabilities and current settings
    4. Print file - Submit a print job with custom options
    
    Key Features:
    - Support for both local and network printers
    - Real-time printer status monitoring
    - Flexible print options (copies, orientation, color, paper size, duplex, etc.)
    - Print job management (status tracking, cancellation)
    - Automatic format conversion between generic and Windows-specific options
    
    Print Options Format:
    Windows uses Device Mode (dmXXX) parameters:
    - dmCopies: Number of copies (integer)
    - dmOrientation: 1=Portrait, 2=Landscape
    - dmColor: 1=Monochrome, 2=Color
    - dmPaperSize: Paper size constant (9=A4, 1=Letter, etc.)
    - dmDuplex: 1=Simplex, 2=Vertical, 3=Horizontal
    - dmDefaultSource: Paper source/bin
    - dmPrintQuality: Print quality (-4=Default, positive values=DPI)
    - dmCollate: 1=Collate, 0=No collate
    
    Usage Tips:
    - Always check printer status before printing
    - Use printer attributes to determine available options
    - Handle errors gracefully (printer offline, paper out, etc.)
    - Monitor print jobs for completion status
    
    """


def get_print_options_format():
    """Get Windows-specific print options format

    Returns:
        dict: Windows print options format and examples
    """
    response = {
        "platform": "Windows",
        "format": "dmXXX (Device Mode parameters)",
        "description": "Windows uses Device Mode (DEVMODE) parameters with dm prefix for print options",
        "documentation": "https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-devmodew",
        "options": {
            "dmCopies": {
                "type": "int",
                "description": "Number of copies to print",
            },
            "dmOrientation": {
                "type": "int",
                "description": "Paper orientation",
                "values": {"1": "Portrait (DMORIENT_PORTRAIT)", "2": "Landscape (DMORIENT_LANDSCAPE)"},
            },
            "dmColor": {
                "type": "int",
                "description": "Color mode",
                "values": {"1": "Monochrome (DMCOLOR_MONOCHROME)", "2": "Color (DMCOLOR_COLOR)"},
            },
            "dmPaperSize": {
                "type": "int",
                "description": "Paper size constant, see: https://learn.microsoft.com/en-us/windows/win32/intl/paper-sizes",
                "common_values": {
                    "1": "Letter (DMPAPER_LETTER)",
                    "5": "Legal (DMPAPER_LEGAL)",
                    "8": "A3 (DMPAPER_A3)",
                    "9": "A4 (DMPAPER_A4)",
                    "11": "A5 (DMPAPER_A5)",
                    "12": "B4 (DMPAPER_B4)",
                    "13": "B5 (DMPAPER_B5)",
                    "7": "Executive (DMPAPER_EXECUTIVE)",
                    "14": "Folio (DMPAPER_FOLIO)",
                },
            },
            "dmDuplex": {
                "type": "int",
                "description": "Duplex (double-sided) printing mode",
                "values": {
                    "1": "Simplex (DMDUP_SIMPLEX)",
                    "2": "Long edge (DMDUP_VERTICAL)",
                    "3": "Short edge (DMDUP_HORIZONTAL)",
                },
            },
            "dmDefaultSource": {
                "type": "int",
                "description": "Paper source/bin, device-specific values",
            },
            "dmMediaType": {
                "type": "int",
                "description": "Media type, device-specific values",
            },
            "dmPrintQuality": {
                "type": "int",
                "description": "Print quality. Negative values are predefined, positive values are DPI",
                "predefined_values": {
                    "-1": "Draft (DMRES_DRAFT)",
                    "-2": "Low (DMRES_LOW)",
                    "-3": "Medium (DMRES_MEDIUM)",
                    "-4": "High (DMRES_HIGH)",
                },
            },
            "dmCollate": {
                "type": "int",
                "description": "Collation mode",
                "values": {"0": "No collate", "1": "Collate (DMCOLLATE_TRUE)"},
            },
            "dmPaperLength": {
                "type": "int",
                "description": "Custom paper length in tenths of a millimeter, overrides dmPaperSize",
            },
            "dmPaperWidth": {
                "type": "int",
                "description": "Custom paper width in tenths of a millimeter, overrides dmPaperSize",
            },
        },
        "examples": {
            "basic_print": {
                "dmCopies": 1,
                "dmOrientation": 1,
                "dmColor": 1,
                "dmPaperSize": 9,
            },
            "advanced_print": {
                "dmCopies": 2,
                "dmOrientation": 2,
                "dmColor": 2,
                "dmPaperSize": 9,
                "dmDuplex": 2,
                "dmDefaultSource": 7,
                "dmPrintQuality": -4,
                "dmCollate": 1,
            },
        },
    }
    return response





def get_printer_list() -> Dict[str, Any]:
    """Get the list of printers on Windows"""
    try:
        # Get local and network printers
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        printer_list: List[Printer] = []

        # Get default printer name
        default_printer = None
        try:
            default_printer = win32print.GetDefaultPrinter()
        except Exception:
            pass

        index = 0
        for printer in printers:
            index += 1
            printer_name = printer[2]

            # Get printer detailed information
            try:
                # Open printer handle
                printer_handle = win32print.OpenPrinter(printer_name)
                printer_info = win32print.GetPrinter(printer_handle, 2)

                # Get printer status
                status = PrinterStatus.UNKNOWN
                status_reasons = []
                is_accepting = True

                # Set status based on printer state
                if printer_info["Status"] == 0:
                    status = PrinterStatus.IDLE
                elif printer_info["Status"] & win32print.PRINTER_STATUS_BUSY:
                    status = PrinterStatus.PROCESSING
                elif printer_info["Status"] & (
                    win32print.PRINTER_STATUS_ERROR
                    | win32print.PRINTER_STATUS_OFFLINE
                    | win32print.PRINTER_STATUS_PAUSED
                ):
                    status = PrinterStatus.STOPPED
                    is_accepting = False

                # Get status reasons
                if printer_info["Status"] & win32print.PRINTER_STATUS_PAUSED:
                    status_reasons.append("paused")
                if printer_info["Status"] & win32print.PRINTER_STATUS_ERROR:
                    status_reasons.append("error")
                if printer_info["Status"] & win32print.PRINTER_STATUS_OFFLINE:
                    status_reasons.append("offline")
                if printer_info["Status"] & win32print.PRINTER_STATUS_PAPER_OUT:
                    status_reasons.append("out-of-paper")
                if printer_info["Status"] & win32print.PRINTER_STATUS_PAPER_JAM:
                    status_reasons.append("paper-jam")
                if printer_info["Status"] & win32print.PRINTER_STATUS_DOOR_OPEN:
                    status_reasons.append("door-open")
                if printer_info["Status"] & win32print.PRINTER_STATUS_TONER_LOW:
                    status_reasons.append("toner-low")
                if printer_info["Status"] & win32print.PRINTER_STATUS_NO_TONER:
                    status_reasons.append("no-toner")

                printer_obj = Printer(
                    index=index,
                    name=printer_name,
                    status=status,
                    status_reasons=status_reasons,
                    is_accepting=is_accepting,
                    type=printer_info.get("pDriverName", "Unknown"),
                    is_default=(printer_name == default_printer),
                    location=printer_info.get("pLocation", ""),
                    model=printer_info.get("pDriverName", ""),
                    uri=printer_info.get("pPortName", ""),
                    driver=printer_info.get("pDriverName", ""),
                    port=printer_info.get("pPortName", ""),
                    job_count=printer_info.get("cJobs", 0),
                )

                win32print.ClosePrinter(printer_handle)
                printer_list.append(printer_obj)
            except Exception as e:
                logger.error(f"Error getting details for printer {printer_name}: {e}")

        printer_dicts = [printer.to_dict() for printer in printer_list]

        response = APIResponse.success(
            {
                "printers": printer_dicts,
                "count": len(printer_list),
            }
        )
        return response.to_dict()
    except Exception as e:
        logger.error(f"Error getting printer list: {e}")
        response = APIResponse.server_error(
            f"Error getting printer list: {str(e)}", {"printers": [], "count": 0}
        )
        return response.to_dict()


def get_index_printer_from_list(index: int) -> Optional[Printer]:
    """Get printer by index from printer list

    Args:
        index: Printer index (1-based)

    Returns:
        Printer object if found, None otherwise
    """
    printer_result = get_printer_list()
    if printer_result["code"] != 200:
        return None
    printer_list = printer_result["data"]["printers"]
    for printer_data in printer_list:
        if printer_data["index"] == index:
            return Printer.from_dict(printer_data)
    return None


def get_printer_status(index: int) -> Dict[str, Any]:
    """Get printer status by index

    Args:
        index: Printer index (1-based)

    Returns:
        dict: Printer status information following CUPS format
    """
    printer = get_index_printer_from_list(index)
    if printer is None:
        response = APIResponse.not_found("Printer not found")
        return response.to_dict()

    try:
        # Directly use printer data from the list
        response = APIResponse.success(
            {
                "index": printer.index,
                "name": printer.name,
                "is_accepting_jobs": printer.is_accepting,
                "status_reasons": printer.status_reasons,
                "status": printer.status.value,
            }
        )
        return response.to_dict()

    except Exception as e:
        response = APIResponse.server_error(f"Error getting printer status: {str(e)}")
        return response.to_dict()


def get_dev_mode(devmode, printer_name):
    dev_mode = {}
    for attr in devmode.__dir__():
        if attr.startswith("_"):
            continue
        elif isinstance(getattr(devmode, attr), int):
            dev_mode[attr] = getattr(devmode, attr)

    has_color = False
    try:
        if (
            win32print.DeviceCapabilities(
                printer_name, "FILE:", win32con.DC_COLORDEVICE
            )
            == 1
        ):
            has_color = True
    except Exception as e:
        logger.error("errors", "[get_dev_mode] error: %s", e)

    if not has_color and dev_mode["Color"] != 1:
        dev_mode["Color"] = 1

    return dev_mode


def get_capabilities_dict(printer_name, port, dc_names, dc_values):
    data = {}
    try:
        name = win32print.DeviceCapabilities(printer_name, port, dc_names)
        val = win32print.DeviceCapabilities(printer_name, port, dc_values)
    except pywintypes.error as e:
        print(dc_names, dc_values, e)
        return {}
    for index, name in enumerate(name):
        if not name:
            continue
        data[name] = val[index]
    return data


def get_capabilities(printer_name):
    port = "FILE:"
    capabilities = {
        "Bins": get_capabilities_dict(
            printer_name, port, win32con.DC_BINNAMES, win32con.DC_BINS
        )
    }
    color = {"Black": 1}
    try:
        if (
            win32print.DeviceCapabilities(printer_name, port, win32con.DC_COLORDEVICE)
            == 1
        ):
            color["Color"] = 2
    except pywintypes.error as e:
        # No color option available
        logger.error(printer_name, e)

    capabilities["Color"] = color
    media_types = get_capabilities_dict(
        printer_name, port, win32con.DC_MEDIATYPENAMES, win32con.DC_MEDIATYPES
    )
    capabilities["MediaTypes"] = media_types or {"Default": 0}
    capabilities["Papers"] = get_capabilities_dict(
        printer_name, port, win32con.DC_PAPERNAMES, win32con.DC_PAPERS
    )
    try:
        max_copies = win32print.DeviceCapabilities(
            printer_name, port, win32con.DC_COPIES
        )
    except pywintypes.error as e:
        logger.error("max_copies, error: %s" % e)
        max_copies = 99
    capabilities["Copies"] = max_copies if max_copies > 1 else 99
    orientation = {"Portrait": 1, "Landscape": 2}
    capabilities["Orientation"] = orientation
    duplex = {"Off": 1}
    if win32print.DeviceCapabilities(printer_name, port, win32con.DC_DUPLEX) == 1:
        duplex["Long Edge"] = 2
        duplex["Short Edge"] = 3
    capabilities["Duplex"] = duplex
    return capabilities


def get_printer_attrs(index: int):
    printer = get_index_printer_from_list(index)
    if printer is None:
        response = APIResponse.not_found("Printer not found")
        return response.to_dict()
    printer_name = printer.name
    try:
        p = win32print.OpenPrinter(printer_name)
    except pywintypes.error as e:
        logger.error("open_printer_fail: %s", e)
        return APIResponse.error(500, "get printer params error, err: %s" % e).to_dict()
    try:
        printer = win32print.GetPrinter(p, 2)
        devmode = printer["pDevMode"]
        dev_mode = get_dev_mode(devmode, printer_name)
        capabilities = get_capabilities(printer_name)
    except (win32ui.error, Exception) as e:
        logger.error("[get_printer_params] error: %s", e)
        return APIResponse.error(500, "get printer params error, err: %s" % e).to_dict()

    data = {
        "Capabilities": capabilities,
        "DevMode": dev_mode,
        "Name": printer_name,
    }

    win32print.ClosePrinter(p)
    result = APIResponse.success(data)
    return result.to_dict()


def get_print_jobs(printer_name: str = None) -> Dict[str, Any]:
    """Get print jobs for a specific printer or all printers

    Args:
        printer_name: Printer name. If None, get jobs from all printers

    Returns:
        dict: Print jobs information
    """
    try:
        all_jobs = []

        if printer_name:
            # Get jobs for specific printer
            printer_names = [printer_name]
        else:
            # Get jobs for all printers
            printer_result = get_printer_list()
            if printer_result["code"] != 200:
                return printer_result
            printer_names = [p["name"] for p in printer_result["data"]["printers"]]

        for pname in printer_names:
            try:
                # Open printer handle
                printer_handle = win32print.OpenPrinter(pname)

                # Enumerate print jobs
                jobs = win32print.EnumJobs(printer_handle, 0, -1, 1)

                for job in jobs:
                    # Map job status to string
                    status_map = {
                        0: "queued",
                        win32print.JOB_STATUS_PAUSED: "paused",
                        win32print.JOB_STATUS_ERROR: "error",
                        win32print.JOB_STATUS_DELETING: "canceling",
                        win32print.JOB_STATUS_SPOOLING: "spooling",
                        win32print.JOB_STATUS_PRINTING: "printing",
                        win32print.JOB_STATUS_OFFLINE: "offline",
                        win32print.JOB_STATUS_PAPEROUT: "out-of-paper",
                        win32print.JOB_STATUS_PRINTED: "completed",
                        win32print.JOB_STATUS_DELETED: "canceled",
                        win32print.JOB_STATUS_BLOCKED_DEVQ: "blocked",
                        win32print.JOB_STATUS_USER_INTERVENTION: "user-intervention",
                        win32print.JOB_STATUS_RESTART: "restart",
                    }

                    job_status = "unknown"
                    for status_flag, status_name in status_map.items():
                        if job.get("Status", 0) & status_flag:
                            job_status = status_name
                            break
                    if job.get("Status", 0) == 0:
                        job_status = "queued"

                    print_job = PrintJob(
                        job_id=job.get("JobId", 0),
                        printer_name=pname,
                        job_name=job.get("pDocument", "Unknown"),
                        status=job_status,
                        priority=job.get("Priority", 0),
                        size=job.get("Size", 0),
                        pages=job.get("PagesPrinted", 0),
                        user=job.get("pUserName", ""),
                        submitted_time=job.get("Submitted", 0),
                        total_pages=job.get("TotalPages", 0),
                        pages_printed=job.get("PagesPrinted", 0),
                    )
                    all_jobs.append(print_job.to_dict())

                win32print.ClosePrinter(printer_handle)

            except Exception as e:
                logger.error(f"Error getting jobs for printer {pname}: {e}")
                continue

        response = APIResponse.success({"jobs": all_jobs, "count": len(all_jobs)})
        return response.to_dict()

    except Exception as e:
        logger.error(f"Error getting print jobs: {e}")
        response = APIResponse.server_error(f"Error getting print jobs: {str(e)}")
        return response.to_dict()


def get_print_job_status(job_id: int) -> Dict[str, Any]:
    """Get print job status by job ID

    Args:
        job_id: Print job ID

    Returns:
        dict: Job status information
    """
    try:
        # Get all jobs and find the one with matching job_id
        jobs_result = get_print_jobs()
        if jobs_result["code"] != 200:
            return jobs_result

        jobs = jobs_result["data"]["jobs"]
        for job in jobs:
            if job["job_id"] == job_id:
                response = APIResponse.success(job)
                return response.to_dict()

        # Job not found
        response = APIResponse.not_found(f"Print job {job_id} not found")
        return response.to_dict()

    except Exception as e:
        logger.error(f"Error getting job status for job {job_id}: {e}")
        response = APIResponse.server_error(f"Error getting job status: {str(e)}")
        return response.to_dict()


def cancel_print_job(job_id: int) -> Dict[str, Any]:
    """Cancel a print job by job ID

    Args:
        job_id: Print job ID to cancel

    Returns:
        dict: Response indicating success or failure
    """
    try:
        # First, find the job to get the printer name
        job_status_result = get_print_job_status(job_id)
        if job_status_result["code"] != 200:
            return job_status_result

        job_info = job_status_result["data"]
        printer_name = job_info["printer_name"]

        # Open printer handle
        printer_handle = win32print.OpenPrinter(printer_name)

        try:
            # Cancel the specific job
            win32print.SetJob(
                printer_handle, job_id, 0, None, win32print.JOB_CONTROL_CANCEL
            )

            response = APIResponse.success(
                {"job_id": job_id, "printer_name": printer_name, "status": "canceled"}
            )
            return response.to_dict()

        finally:
            win32print.ClosePrinter(printer_handle)

    except pywintypes.error as e:
        logger.error(f"Windows API error canceling job {job_id}: {e}")
        response = APIResponse.server_error(f"Windows API error: {str(e)}")
        return response.to_dict()
    except Exception as e:
        logger.error(f"Error canceling job {job_id}: {e}")
        response = APIResponse.server_error(f"Error canceling job: {str(e)}")
        return response.to_dict()


def set_dev_mode(devmode, options: WindowsPrintOptions):
    """Set device mode parameters from WindowsPrintOptions

    Args:
        devmode: Windows device mode object
        options: WindowsPrintOptions instance
    """
    if not options:
        return

    # Set device mode fields
    fields_to_set = 0

    if options.dmOrientation is not None:
        fields_to_set |= win32con.DM_ORIENTATION
        devmode.Orientation = int(options.dmOrientation)

    if options.dmCopies is not None:
        fields_to_set |= win32con.DM_COPIES
        devmode.Copies = int(options.dmCopies)

    if options.dmColor is not None:
        fields_to_set |= win32con.DM_COLOR
        devmode.Color = int(options.dmColor)

    if options.dmPaperSize is not None:
        fields_to_set |= win32con.DM_PAPERSIZE
        devmode.PaperSize = int(options.dmPaperSize)

    if options.dmDuplex is not None:
        fields_to_set |= win32con.DM_DUPLEX
        devmode.Duplex = int(options.dmDuplex)

    if options.dmDefaultSource is not None:
        fields_to_set |= win32con.DM_DEFAULTSOURCE
        devmode.DefaultSource = int(options.dmDefaultSource)

    if options.dmMediaType is not None:
        fields_to_set |= win32con.DM_MEDIATYPE
        devmode.MediaType = int(options.dmMediaType)

    if options.dmPrintQuality is not None:
        fields_to_set |= win32con.DM_PRINTQUALITY
        devmode.PrintQuality = int(options.dmPrintQuality)

    if options.dmCollate is not None:
        fields_to_set |= win32con.DM_COLLATE
        devmode.Collate = int(options.dmCollate)

    # Handle custom paper size
    if options.dmPaperSize == 0 or options.dmPaperSize is None:
        if options.dmPaperLength is not None:
            fields_to_set |= win32con.DM_PAPERLENGTH
            devmode.PaperLength = int(options.dmPaperLength)

        if options.dmPaperWidth is not None:
            fields_to_set |= win32con.DM_PAPERWIDTH
            devmode.PaperWidth = int(options.dmPaperWidth)

    # Apply all fields at once
    devmode.Fields = devmode.Fields | fields_to_set


def print_file(index: int, file_path: str, options: Optional[WindowsPrintOptions] = None):
    printer = get_index_printer_from_list(index)
    if printer is None:
        response = APIResponse.not_found("Printer not found")
        return response.to_dict()
    printer_name = printer.name
    try:
        p = win32print.OpenPrinter(printer_name)
    except pywintypes.error as e:
        logger.error("open_printer_fail: %s", e)
        return APIResponse.error(500, "open printer error, err: %s" % e).to_dict()

    try:
        printer = win32print.GetPrinter(p, 2)
        devmode = printer["pDevMode"]
        set_dev_mode(devmode, options)
    except Exception as e:
        logger.error(
            "print_prn set_dev_mode_fail, error: %s, devmode: %s, printer_model: %s",
            e,
            devmode,
            printer_name,
        )
        win32print.ClosePrinter(p)
        return APIResponse.server_error(f"Error printing file: {str(e)}").to_dict()

    win32print.DocumentProperties(
        0,
        p,
        printer_name,
        devmode,
        devmode,
        win32con.DM_IN_BUFFER | win32con.DM_OUT_BUFFER,
    )

    job_id = None
    try:
        # Read file content as bytes
        with open(file_path, "rb") as f:
            file_content = f.read()

        doc_info = (file_path, None, "RAW")
        job_id = win32print.StartDocPrinter(p, 1, doc_info)
        win32print.StartPagePrinter(p)
        win32print.WritePrinter(p, file_content)
        win32print.EndPagePrinter(p)
        win32print.EndDocPrinter(p)
    except Exception as e:
        logger.error(f"Error printing file {file_path}: {e}")
        return APIResponse.server_error(f"Error printing file: {str(e)}").to_dict()
    finally:
        win32print.ClosePrinter(p)

    # If we get here, printing was successful
    response = APIResponse.success(
        {
            "printer_name": printer_name,
            "file_path": file_path,
            "status": "submitted",
            "job_id": job_id,
        }
    )
    return response.to_dict()
