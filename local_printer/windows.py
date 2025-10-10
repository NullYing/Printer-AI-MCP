"""
Windows Printer Operations Module
"""
import subprocess
import json
from typing import Dict, Any
from models.model import APIResponse, PrinterStatus


def print_file_prompt():
    return """
    Windows Printer Operations Module
    
    1. First get the printer list
    2. Then get the printer status
    3. Then get printer attrs
    4. Then print the file with the printer attrs
    
    """


def get_printer_list() -> Dict[str, Any]:
    """Get the list of printers on Windows"""
    try:
        # Use PowerShell to get printer list
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Printer | Select-Object Name, DriverName, PortName, PrinterStatus | ConvertTo-Json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            printers = json.loads(result.stdout) if result.stdout.strip() else []
            
            # If there's only one printer, PowerShell returns an object instead of an array
            if isinstance(printers, dict):
                printers = [printers]
            
            # Add index to each printer
            for index, printer in enumerate(printers, start=1):
                printer['Index'] = index
            
            response = APIResponse.success({
                "printers": printers,
                "count": len(printers) if isinstance(printers, list) else 0
            })
            return response.to_dict()
        else:
            response = APIResponse.server_error(f"Failed to get printer list: {result.stderr}", {"printers": [], "count": 0})
            return response.to_dict()
    except Exception as e:
        response = APIResponse.server_error(f"Error getting printer list: {str(e)}", {"printers": [], "count": 0})
        return response.to_dict()


def get_printer_status(index: int = None) -> Dict[str, Any]:
    """Get printer status by index
    
    Args:
        index: Printer index (1-based). If None, returns the default printer status
    """
    try:
        # Get printer list first
        printers_result = get_printer_list()
        
        if printers_result["code"] != 200:
            return printers_result
        
        printers = printers_result["data"]["printers"]
        
        if not printers:
            response = APIResponse.not_found("No printers found")
            return response.to_dict()
        
        # Determine which printer to query
        printer = None
        
        if index is None:
            # Get default printer
            result = subprocess.run(
                ['powershell', '-Command', '(Get-WmiObject -Class Win32_Printer | Where-Object {$_.Default -eq $true}).Name'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                default_name = result.stdout.strip()
                printer = next((p for p in printers if p.get('Name') == default_name), printers[0])
            else:
                # If no default, use the first printer
                printer = printers[0]
        else:
            # Use printer by index (1-based)
            if index < 1 or index > len(printers):
                response = APIResponse.error(400, f"Invalid printer index. Valid range: 1-{len(printers)}")
                return response.to_dict()
            printer = printers[index - 1]
        
        # Get detailed printer status
        printer_name = printer.get('Name', '')
        result = subprocess.run(
            ['powershell', '-Command', f'Get-Printer -Name "{printer_name}" | Select-Object Name, PrinterStatus, JobCount, DriverName, PortName, Location | ConvertTo-Json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            detailed_status = json.loads(result.stdout)
            
            # Convert Windows printer status to PrinterStatus enum
            windows_status = detailed_status.get('PrinterStatus', 'Unknown')
            status = PrinterStatus.from_string(windows_status)
            
            response = APIResponse.success({
                "name": detailed_status.get('Name', ''),
                "index": index if index else printer.get('Index', 1),
                "status": status.value,
                "job_count": detailed_status.get('JobCount', 0),
                "driver": detailed_status.get('DriverName', ''),
                "port": detailed_status.get('PortName', ''),
                "location": detailed_status.get('Location', '')
            })
            return response.to_dict()
        else:
            response = APIResponse.server_error(f"Failed to get printer status: {result.stderr}")
            return response.to_dict()
    except Exception as e:
        response = APIResponse.server_error(f"Error getting printer status: {str(e)}")
        return response.to_dict()
