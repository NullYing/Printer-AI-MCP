"""
Cups Printer Operations Module
"""

import cups
from typing import List, Dict, Any, Optional
from models.model import (
    Printer,
    APIResponse,
    PrintOptions,
    PrinterStatus,
    PrintJob,
    LinuxPrintOptions,
)
from utils.logger import logger


def print_file_prompt():
    return """
    CUPS Printer Operations Module
    
    This module provides comprehensive printer management capabilities for Linux/macOS systems using CUPS (Common UNIX Printing System) and IPP (Internet Printing Protocol).
    
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
    - Automatic format conversion between generic and CUPS-specific options
    
    Print Options Format:
    CUPS uses IPP standard parameters:
    - copies: Number of copies (string, e.g., "2")
    - media: Paper size (e.g., "A4", "Letter", "Legal")
    - orientation_requested: "3"=Portrait, "4"=Landscape
    - print_color_mode: "monochrome" or "color"
    - sides: "one-sided", "two-sided-long-edge", "two-sided-short-edge"
    - print_quality: "3"=Draft, "4"=Normal, "5"=High
    - page_ranges: Specific pages (e.g., "1-5,10-15")
    - number_up: Pages per sheet (e.g., "2")
    
    Usage Tips:
    - Always check printer status before printing
    - Use printer attributes to determine available options
    - Handle errors gracefully (printer offline, paper out, etc.)
    - Monitor print jobs for completion status
    - Printer attributes contain all available options and current settings
    
    """


def get_print_options_format():
    """Get Linux/CUPS-specific print options format

    Returns:
        dict: Linux/CUPS print options format and examples
    """
    response = {
        "platform": "Linux/macOS",
        "format": "CUPS/IPP (Internet Printing Protocol)",
        "description": "Linux/macOS uses CUPS with IPP standard options",
        "examples": {
            "basic_print": {
                "copies": "1",
                "media": "A4",
                "orientation_requested": "3",  # 3=Portrait, 4=Landscape
                "print_color_mode": "monochrome",
            },
            "advanced_print": {
                "copies": "2",
                "media": "A4",
                "orientation_requested": "4",  # Landscape
                "print_color_mode": "color",
                "sides": "two-sided-long-edge",  # Duplex
                "print_quality": "4",  # 3=Draft, 4=Normal, 5=High
                "page_ranges": "1-5,10-15",  # Specific pages
                "number_up": "2",  # Pages per sheet
            },
        },
        "media_sizes": ["A3", "A4", "A5", "Letter", "Legal", "Executive"],
        "orientations": {"Portrait": "3", "Landscape": "4"},
        "color_modes": ["monochrome", "color"],
        "duplex_modes": [
            "one-sided",
            "two-sided-long-edge",
            "two-sided-short-edge",
        ],
        "quality_levels": {"Draft": "3", "Normal": "4", "High": "5"},
    }
    return response


def convert_print_options(options: dict, target_format: str = "auto"):
    """Convert print options between different formats for Linux/CUPS

    Args:
        options: Print options dictionary
        target_format: Target format ('linux', 'generic', 'auto')

    Returns:
        dict: Converted print options
    """
    if not options:
        response = APIResponse.success(
            {"converted_options": {}, "format": target_format}
        )
        return response.to_dict()

    try:
        # Determine target format
        if target_format == "auto":
            target_format = "linux"

        # Convert options
        if target_format == "linux":
            converted = LinuxPrintOptions.from_generic_options(options)
            converted_dict = converted.to_dict()
        elif target_format == "generic":
            # Convert from CUPS format to generic format
            converted_dict = {}

            # From CUPS format
            if "copies" in options and isinstance(options["copies"], str):
                converted_dict["copies"] = int(options["copies"])
            if "orientation_requested" in options:
                converted_dict["orientation"] = (
                    "portrait"
                    if options["orientation_requested"] == "3"
                    else "landscape"
                )
            if "print_color_mode" in options:
                converted_dict["color_mode"] = options["print_color_mode"]
            if "sides" in options:
                sides_map = {
                    "one-sided": "off",
                    "two-sided-long-edge": "long-edge",
                    "two-sided-short-edge": "short-edge",
                }
                converted_dict["duplex"] = sides_map.get(options["sides"], "off")
            if "media" in options:
                converted_dict["paper_size"] = options["media"]
            if "print_quality" in options:
                quality_map = {"3": "draft", "4": "normal", "5": "high"}
                converted_dict["quality"] = quality_map.get(
                    options["print_quality"], "normal"
                )
        else:
            response = APIResponse.error(400, f"Invalid target format: {target_format}")
            return response.to_dict()

        response = APIResponse.success(
            {
                "original_options": options,
                "converted_options": converted_dict,
                "source_format": "auto-detected",
                "target_format": target_format,
            }
        )
        return response.to_dict()

    except Exception as e:
        response = APIResponse.server_error(f"Error converting options: {str(e)}")
        return response.to_dict()


def get_printer_list() -> Dict[str, Any]:
    """Get the list of printers on macOS (using CUPS)"""
    try:
        # Connect to CUPS server
        conn = cups.Connection()

        # Get all printers
        printers_dict = conn.getPrinters()

        # Get default printer
        default_printer = None
        try:
            default_printer = conn.getDefault()
        except:
            # No default printer set
            pass

        # Build printer list
        printers: List[Printer] = []
        index = 0
        for printer_name, printer_attrs in printers_dict.items():
            index += 1
            # Get printer state
            # printer_attrs['printer-state'] values:
            # 3 = idle, 4 = processing, 5 = stopped
            state = printer_attrs.get("printer-state", 3)
            state_reasons = printer_attrs.get("printer-state-reasons", [])

            # Determine status using PrinterStatus enum
            status = PrinterStatus.from_cups_state(state)

            # Check if printer is accepting jobs
            is_accepting = printer_attrs.get("printer-is-accepting-jobs", True)

            # Check if this is the default printer
            is_default = printer_name == default_printer

            printer = Printer(
                index=index,
                name=printer_name,
                status=status,
                status_reasons=state_reasons,
                is_accepting=is_accepting,
                type="CUPS",
                is_default=is_default,
                location=printer_attrs.get("printer-location", ""),
                model=printer_attrs.get("printer-make-and-model", ""),
                uri=printer_attrs.get("device-uri", ""),
            )
            printers.append(printer)

        # Convert printers to dict for response
        printers_data = [printer.to_dict() for printer in printers]

        response = APIResponse.success(
            {
                "printers": printers_data,
                "count": len(printers),
                "default_printer": default_printer,
            }
        )
        return response.to_dict()

    except RuntimeError as e:
        # CUPS connection error
        response = APIResponse.server_error(
            f"CUPS connection error: {str(e)}", {"printers": [], "count": 0}
        )
        return response.to_dict()
    except Exception as e:
        response = APIResponse.server_error(
            f"Error getting printer list: {str(e)}", {"printers": [], "count": 0}
        )
        return response.to_dict()


def get_index_printer_from_list(index: int) -> Optional[Printer]:
    printer_result = get_printer_list()
    if printer_result["code"] != 200:
        return None
    printer_list = printer_result["data"]["printers"]
    for printer_data in printer_list:
        if printer_data["index"] == index:
            return Printer.from_dict(printer_data)
    return None


def get_printer_status(index: int) -> Dict[str, Any]:
    """Get printer status"""
    printer = get_index_printer_from_list(index)
    if printer is None:
        response = APIResponse.not_found("Printer not found")
        return response.to_dict()

    try:
        # Connect to CUPS server
        conn = cups.Connection()

        # Get printer status
        printer_name = printer.name
        printer_attrs = conn.getPrinterAttributes(printer_name)

        state = printer_attrs.get("printer-state", 3)
        status = PrinterStatus.from_cups_state(state)

        response = APIResponse.success(
            {
                "index": index,
                "name": printer_name,
                "is_accepting_jobs": printer_attrs.get(
                    "printer-is-accepting-jobs", True
                ),
                "status_reasons": printer_attrs.get("printer-state-reasons", []),
                "status": status.value,
            }
        )
        return response.to_dict()
    except Exception as e:
        response = APIResponse.server_error(f"Error getting printer status: {str(e)}")
        return response.to_dict()


def get_printer_attrs(index: int) -> Dict[str, Any]:
    """Get printer attributes"""
    printer_result = get_printer_status(index)
    if printer_result["code"] != 200:
        response = APIResponse.not_found("Printer not found")
        return response.to_dict()

    try:
        conn = cups.Connection()
        printer_name = printer_result["data"]["name"]
        printer_attrs = conn.getPrinterAttributes(printer_name)

        response = APIResponse.success(printer_attrs)
        return response.to_dict()
    except Exception as e:
        response = APIResponse.server_error(
            f"Error getting printer attributes: {str(e)}"
        )
        return response.to_dict()


def print_file(
    index: int, file_path: str, options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Print file using CUPS

    Args:
        index: Printer index
        file_path: Path to the file to print
        title: Print job title (optional)
        options: Print options dict (optional), e.g., {'copies': '2', 'media': 'A4'}

    Returns:
        dict: Response with job_id if successful
    """
    import os

    # Check if file exists
    if not os.path.exists(file_path):
        response = APIResponse.not_found(f"File not found: {file_path}")
        return response.to_dict()

    printer = get_index_printer_from_list(index)
    if printer is None:
        response = APIResponse.not_found("Printer not found")
        return response.to_dict()

    try:
        conn = cups.Connection()
        printer_name = printer.name

        # Get printer attributes and check status
        printer_attrs = conn.getPrinterAttributes(printer_name)
        state = printer_attrs.get("printer-state", 3)
        is_accepting = printer_attrs.get("printer-is-accepting-jobs", True)

        # Check if printer is accepting jobs
        if not is_accepting:
            response = APIResponse.server_error(
                "Printer is not accepting jobs",
                {"printer_name": printer_name, "is_accepting": is_accepting},
            )
            return response.to_dict()

        # Warn if printer is not idle (but still try to print)
        if state == 5:  # stopped
            response = APIResponse.server_error(
                "Printer is stopped, cannot print",
                {
                    "printer_name": printer_name,
                    "state": state,
                    "state_reasons": printer_attrs.get("printer-state-reasons", []),
                },
            )
            return response.to_dict()

        # Prepare print options - convert to CUPS format if needed
        if options:
            # Check if options are already in CUPS format or need conversion
            if not any(
                key
                in [
                    "copies",
                    "media",
                    "orientation_requested",
                    "print_color_mode",
                    "sides",
                ]
                for key in options.keys()
            ):
                # Generic options, convert to CUPS format
                linux_options = LinuxPrintOptions.from_generic_options(options)
                print_options = linux_options.to_dict()
            else:
                print_options = options
        else:
            print_options = {}

        # Set default title if not provided
        title = os.path.basename(file_path)

        # Send print job to CUPS
        logger.info("Printing file: %s", file_path)
        logger.info("Print options: %s", print_options)
        logger.info("Printer name: %s", printer_name)
        logger.info("Title: %s", title)

        job_id = conn.printFile(printer_name, file_path, title, print_options)

        logger.info("Job ID: %s", job_id)

        response = APIResponse.success(
            {
                "job_id": job_id,
                "printer_name": printer_name,
                "file_path": file_path,
                "title": title,
                "status": "submitted",
            }
        )
        return response.to_dict()

    except cups.IPPError as e:
        # CUPS specific errors
        response = APIResponse.server_error(f"CUPS IPP error: {str(e)}")
        return response.to_dict()
    except Exception as e:
        logger.exception("Error printing file: %s", e)
        response = APIResponse.server_error(f"Error printing file: {str(e)}")
        return response.to_dict()


def get_print_jobs(printer_name: str = None) -> Dict[str, Any]:
    """Get print jobs for a specific printer or all printers

    Args:
        printer_name: Printer name. If None, get jobs from all printers

    Returns:
        dict: Print jobs information
    """
    try:
        conn = cups.Connection()

        # Get all jobs
        jobs = conn.getJobs(which_jobs="all", my_jobs=False)

        all_jobs = []
        for job_id, job_info in jobs.items():
            # Filter by printer name if specified
            if printer_name and job_info.get("job-printer-name") != printer_name:
                continue

            # Job state values:
            # 3 = pending, 4 = pending-held, 5 = processing,
            # 6 = processing-stopped, 7 = canceled, 8 = aborted, 9 = completed
            job_state = job_info.get("job-state", 0)
            state_map = {
                3: "pending",
                4: "pending-held",
                5: "processing",
                6: "processing-stopped",
                7: "canceled",
                8: "aborted",
                9: "completed",
            }

            print_job = PrintJob(
                job_id=job_id,
                printer_name=job_info.get("job-printer-name", ""),
                job_name=job_info.get("job-name", ""),
                status=state_map.get(job_state, "unknown"),
                priority=job_info.get("job-priority", 0),
                size=job_info.get("job-k-octets", 0) * 1024,  # Convert KB to bytes
                pages=job_info.get("job-impressions-completed", 0),
                user=job_info.get("job-originating-user-name", ""),
                submitted_time=job_info.get("time-at-creation", 0),
                total_pages=job_info.get("job-impressions", 0),
                pages_printed=job_info.get("job-impressions-completed", 0),
            )
            all_jobs.append(print_job.to_dict())

        response = APIResponse.success({"jobs": all_jobs, "count": len(all_jobs)})
        return response.to_dict()

    except Exception as e:
        response = APIResponse.server_error(f"Error getting print jobs: {str(e)}")
        return response.to_dict()


def get_print_job_status(job_id: int) -> Dict[str, Any]:
    """
    Get print job status

    Args:
        job_id: Print job ID

    Returns:
        dict: Job status information
    """
    try:
        conn = cups.Connection()

        # Get all jobs
        jobs = conn.getJobs(which_jobs="all", my_jobs=True)

        if job_id not in jobs:
            response = APIResponse.not_found(f"Print job {job_id} not found")
            return response.to_dict()

        job = jobs[job_id]

        # Job state values:
        # 3 = pending, 4 = pending-held, 5 = processing,
        # 6 = processing-stopped, 7 = canceled, 8 = aborted, 9 = completed
        job_state = job.get("job-state", 0)
        state_map = {
            3: "pending",
            4: "pending-held",
            5: "processing",
            6: "processing-stopped",
            7: "canceled",
            8: "aborted",
            9: "completed",
        }

        response = APIResponse.success(
            {
                "job_id": job_id,
                "printer_name": job.get("job-printer-name", ""),
                "job_name": job.get("job-name", ""),
                "job_state": state_map.get(job_state, "unknown"),
                "job_state_reasons": job.get("job-state-reasons", []),
                "time_at_creation": job.get("time-at-creation", 0),
                "time_at_processing": job.get("time-at-processing", 0),
                "time_at_completed": job.get("time-at-completed", 0),
            }
        )
        return response.to_dict()

    except Exception as e:
        response = APIResponse.server_error(f"Error getting job status: {str(e)}")
        return response.to_dict()


def cancel_print_job(job_id: int) -> Dict[str, Any]:
    """
    Cancel a print job

    Args:
        job_id: Print job ID to cancel

    Returns:
        dict: Response indicating success or failure
    """
    try:
        conn = cups.Connection()
        conn.cancelJob(job_id)

        response = APIResponse.success({"job_id": job_id, "status": "canceled"})
        return response.to_dict()

    except cups.IPPError as e:
        response = APIResponse.server_error(f"CUPS IPP error: {str(e)}")
        return response.to_dict()
    except Exception as e:
        response = APIResponse.server_error(f"Error canceling job: {str(e)}")
        return response.to_dict()
