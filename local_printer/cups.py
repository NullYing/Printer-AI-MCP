"""
Cups Printer Operations Module
"""
import cups


def print_file_prompt():
    return """
    Print file using CUPS and IPP protocol
    
    1. First get the printer list
    2. Then get the printer status
    3. Then get printer attrs
    4. Then print the file with the printer attrs

    Attention:
    1. The printer attrs is a dict, you can use it to print the file

    """


def get_printer_list():
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
        printers = []
        index = 0
        for printer_name, printer_attrs in printers_dict.items():
            index += 1
            # Get printer state
            # printer_attrs['printer-state'] values:
            # 3 = idle, 4 = processing, 5 = stopped
            state = printer_attrs.get('printer-state', 3)
            state_reasons = printer_attrs.get('printer-state-reasons', [])

            # Determine status
            if state == 3:
                status = 'idle'
            elif state == 4:
                status = 'processing'
            elif state == 5:
                status = 'stopped'
            else:
                status = 'unknown'

            # Check if printer is accepting jobs
            is_accepting = printer_attrs.get('printer-is-accepting-jobs', True)

            # Check if this is the default printer
            is_default = (printer_name == default_printer)

            printers.append({
                "index": index,
                "name": printer_name,
                "status": status,
                "status_reasons": state_reasons,
                "is_accepting": is_accepting,
                "type": "CUPS",
                "is_default": is_default,
                "location": printer_attrs.get('printer-location', ''),
                "model": printer_attrs.get('printer-make-and-model', ''),
                "uri": printer_attrs.get('device-uri', '')
            })

        return {
            "code": 200,
            "msg": "success",
            "data": {
                "printers": printers,
                "count": len(printers),
                "default_printer": default_printer
            }
        }
    except RuntimeError as e:
        # CUPS connection error
        return {
            "code": 500,
            "msg": f"CUPS connection error: {str(e)}",
            "data": {"printers": [], "count": 0}
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"Error getting printer list: {str(e)}",
            "data": {"printers": [], "count": 0}
        }


def get_index_printer_from_list(index: int):
    printer_result = get_printer_list()
    if printer_result["code"] != 200:
        return None
    printer_list = printer_result["data"]["printers"]
    for printer in printer_list:
        if printer["index"] == index:
            return printer
    return None


def get_printer_status(index: int) -> dict:
    """Get printer status"""
    printer = get_index_printer_from_list(index)
    if printer is None:
        return {
            "code": 404,
            "msg": "Printer not found",
            "data": {}
        }
    try:
        # Connect to CUPS server
        conn = cups.Connection()

        # Get printer status
        printer_name = printer["name"]
        printer_attrs = conn.getPrinterAttributes(printer_name)

        state = printer_attrs.get('printer-state', 3)
        if state == 3:
            status = 'idle'
        elif state == 4:
            status = 'processing'
        elif state == 5:
            status = 'stopped'
        else:
            status = 'unknown'

        return {
            "code": 200,
            "msg": "success",
            "data": {
                "index": index,
                "name": printer_name,
                "is_accepting_jobs": printer_attrs.get('printer-is-accepting-jobs', True),
                "status_reasons": printer_attrs.get('printer-state-reasons', []),
                "status": status
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"Error getting printer status: {str(e)}",
            "data": {}
        }


def get_printer_attrs(index: int) -> dict:
    """Get printer attributes"""
    printer_result = get_printer_status(index)
    if printer_result["code"] != 200:
        return {
            "code": 404,
            "msg": "Printer not found",
        }
    try:
        conn = cups.Connection()

        printer_name = printer_result["data"]["name"]
        printer_attrs = conn.getPrinterAttributes(printer_name)
    except Exception as e:
        return {
            "code": 500,
            "msg": f"Error getting printer attributes: {str(e)}",
        }
    return {
        "code": 200,
        "msg": "success",
        "data": printer_attrs
    }


def print_file(index: int, file_path: str, title: str = "", options: dict = None) -> dict:
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
        return {
            "code": 404,
            "msg": f"File not found: {file_path}",
        }
    
    printer = get_index_printer_from_list(index)
    if printer is None:
        return {
            "code": 404,
            "msg": "Printer not found",
        }
    
    try:
        conn = cups.Connection()
        printer_name = printer["name"]
        
        # Get printer attributes and check status
        printer_attrs = conn.getPrinterAttributes(printer_name)
        state = printer_attrs.get('printer-state', 3)
        is_accepting = printer_attrs.get('printer-is-accepting-jobs', True)
        
        # Check if printer is accepting jobs
        if not is_accepting:
            return {
                "code": 500,
                "msg": "Printer is not accepting jobs",
                "data": {
                    "printer_name": printer_name,
                    "is_accepting": is_accepting
                }
            }
        
        # Warn if printer is not idle (but still try to print)
        if state == 5:  # stopped
            return {
                "code": 500,
                "msg": f"Printer is stopped, cannot print",
                "data": {
                    "printer_name": printer_name,
                    "state": state,
                    "state_reasons": printer_attrs.get('printer-state-reasons', [])
                }
            }
        
        # Prepare print options
        print_options = options if options else {}
        
        # Set default title if not provided
        if not title:
            title = os.path.basename(file_path)
        
        # Send print job to CUPS
        job_id = conn.printFile(printer_name, file_path, title, print_options)
        
        return {
            "code": 200,
            "msg": "success",
            "data": {
                "job_id": job_id,
                "printer_name": printer_name,
                "file_path": file_path,
                "title": title,
                "status": "submitted"
            }
        }
        
    except cups.IPPError as e:
        # CUPS specific errors
        return {
            "code": 500,
            "msg": f"CUPS IPP error: {str(e)}",
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"Error printing file: {str(e)}",
        }


def get_print_job_status(job_id: int) -> dict:
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
        jobs = conn.getJobs(which_jobs='all', my_jobs=True)
        
        if job_id not in jobs:
            return {
                "code": 404,
                "msg": f"Print job {job_id} not found",
            }
        
        job = jobs[job_id]
        
        # Job state values:
        # 3 = pending, 4 = pending-held, 5 = processing,
        # 6 = processing-stopped, 7 = canceled, 8 = aborted, 9 = completed
        job_state = job.get('job-state', 0)
        state_map = {
            3: 'pending',
            4: 'pending-held',
            5: 'processing',
            6: 'processing-stopped',
            7: 'canceled',
            8: 'aborted',
            9: 'completed'
        }
        
        return {
            "code": 200,
            "msg": "success",
            "data": {
                "job_id": job_id,
                "printer_name": job.get('job-printer-name', ''),
                "job_name": job.get('job-name', ''),
                "job_state": state_map.get(job_state, 'unknown'),
                "job_state_reasons": job.get('job-state-reasons', []),
                "time_at_creation": job.get('time-at-creation', 0),
                "time_at_processing": job.get('time-at-processing', 0),
                "time_at_completed": job.get('time-at-completed', 0),
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "msg": f"Error getting job status: {str(e)}",
        }


def cancel_print_job(job_id: int) -> dict:
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
        
        return {
            "code": 200,
            "msg": "success",
            "data": {
                "job_id": job_id,
                "status": "canceled"
            }
        }
        
    except cups.IPPError as e:
        return {
            "code": 500,
            "msg": f"CUPS IPP error: {str(e)}",
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"Error canceling job: {str(e)}",
        }

