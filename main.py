from sys import platform
from mcp.server.fastmcp import FastMCP, Context
from models.model import APIResponse

# Import the corresponding printer module based on the system platform
if platform == "win32":
    from local_printer.windows import get_printer_list as _get_printer_list
    from local_printer.windows import get_printer_status as _get_printer_status
    from local_printer.windows import print_file_prompt as _print_file_prompt
elif platform == "linux" or platform == "darwin":
    from local_printer.cups import get_printer_list as _get_printer_list
    from local_printer.cups import get_printer_status as _get_printer_status
    from local_printer.cups import get_printer_attrs as _get_printer_attrs
    from local_printer.cups import print_file as _print_file
    from local_printer.cups import get_print_job_status as _get_print_job_status
    from local_printer.cups import cancel_print_job as _cancel_print_job
    from local_printer.cups import print_file_prompt as _print_file_prompt
else:
    _get_printer_list = None
    _get_printer_status = None
    _get_printer_attrs = None
    _print_file = None
    _get_print_job_status = None
    _cancel_print_job = None
    _print_file_prompt = None


# Create MCP server
mcp = FastMCP("PrinterAIMCP",
              website_url="https://github.com/NullYing/printer-ai-mcp")


@mcp.tool()
def get_printer_list() -> dict:
    """Get system printer list"""
    if _get_printer_list is None:
        response = APIResponse.server_error(f"Unsupported operating system: {platform}", {"printers": [], "count": 0})
        return response.to_dict()
    
    data_list = _get_printer_list()
    return data_list


@mcp.tool()
def printer_status(ctx: Context, index: int = None) -> dict:
    """Get printer status by index
    
    Args:
        index: Printer index (1-based). If None, returns the default printer status
    """
    if _get_printer_status is None:
        response = APIResponse.server_error(f"Unsupported operating system: {platform}")
        return response.to_dict()
    
    return _get_printer_status(index)


@mcp.tool()
def printer_attrs(ctx: Context, index: int = None) -> dict:
    if _get_printer_attrs is None:
        response = APIResponse.server_error(f"Unsupported operating system: {platform}")
        return response.to_dict()
    return _get_printer_attrs(index)


@mcp.tool()
def print_file(ctx: Context, index: int = None, file_path: str = None, options: dict = None) -> dict:
    """Print file using printer
    
    Args:
        index: Printer index
        file_path: Path to the file to print
        options: Print options dict (optional), e.g., {'copies': '2', 'media': 'A4'}
    """

    if _print_file is None:
        response = APIResponse.server_error(f"Unsupported operating system: {platform}")
        return response.to_dict()
    return _print_file(index, file_path, options)


@mcp.tool()
def get_print_job_status(ctx: Context, job_id: int) -> dict:
    """Get print job status by job id"""
    if _get_print_job_status is None:
        response = APIResponse.server_error(f"Unsupported operating system: {platform}")
        return response.to_dict()
    return _get_print_job_status(job_id)


@mcp.tool()
def cancel_print_job(ctx: Context, job_id: int) -> dict:
    """Cancel print job by job id"""
    if _cancel_print_job is None:
        response = APIResponse.server_error(f"Unsupported operating system: {platform}")
        return response.to_dict()
    return _cancel_print_job(job_id)


@mcp.prompt()
def print_file_prompt():
  return _print_file_prompt()


if __name__ == '__main__':
    mcp.run(transport="streamable-http")
