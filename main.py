from sys import platform
import json
from mcp.server.fastmcp import FastMCP, Context
from models.model import APIResponse

# Import the corresponding printer module based on the system platform
if platform == "win32":
    from local_printer.windows import (
        get_printer_list as _get_printer_list,
        get_printer_status as _get_printer_status,
        get_printer_attrs as _get_printer_attrs,
        print_file as _print_file,
        get_print_jobs as _get_print_jobs,
        get_print_job_status as _get_print_job_status,
        cancel_print_job as _cancel_print_job,
        print_file_prompt as _print_file_prompt,
        get_print_options_format as _get_print_options_format,
        # convert_print_options as _convert_print_options,
    )
elif platform == "linux" or platform == "darwin":
    from local_printer.cups import (
        get_printer_list as _get_printer_list,
        get_printer_status as _get_printer_status,
        get_printer_attrs as _get_printer_attrs,
        print_file as _print_file,
        get_print_jobs as _get_print_jobs,
        get_print_job_status as _get_print_job_status,
        cancel_print_job as _cancel_print_job,
        print_file_prompt as _print_file_prompt,
        get_print_options_format as _get_print_options_format,
        # convert_print_options as _convert_print_options,
    )
else:
    _get_printer_list = None
    _get_printer_status = None
    _get_printer_attrs = None
    _print_file = None
    _get_print_jobs = None
    _get_print_job_status = None
    _cancel_print_job = None
    _print_file_prompt = None
    _get_print_options_format = None
    # _convert_print_options = None


# Create MCP server
mcp = FastMCP(
    "PrinterAIMCP",
    website_url="https://github.com/NullYing/printer-ai-mcp",
)


@mcp.tool()
def get_printer_list() -> dict:
    """Get system printer list"""
    if _get_printer_list is None:
        response = APIResponse.server_error(
            f"Unsupported operating system: {platform}", {"printers": [], "count": 0}
        )
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
def print_file(
    ctx: Context, index: int = None, file_path: str = None, options: dict = None
) -> dict:
    """Print file using printer

    Args:
        index: Printer index (1-based). If None, uses the default printer
        file_path: Path to the file to print
        options: Print options dict (optional)

    Print Options Format:
        Windows (dmXXX format):
            {
                'dmCopies': 2,                    # Number of copies
                'dmOrientation': 1,               # 1=Portrait, 2=Landscape
                'dmColor': 2,                     # 1=Monochrome, 2=Color
                'dmPaperSize': 9,                 # Paper size (9=A4, 1=Letter, etc.)
                'dmDuplex': 1,                    # 1=Simplex, 2=Vertical, 3=Horizontal
                'dmDefaultSource': 7,             # Paper source/bin
                'dmMediaType': 0,                 # Media type
                'dmPrintQuality': -4,             # Print quality
                'dmCollate': 1                    # 1=Collate, 0=No collate
            }

        Linux/CUPS (IPP format):
            {
                'copies': '2',                    # Number of copies as string
                'media': 'A4',                    # Paper size
                'orientation_requested': '3',     # '3'=Portrait, '4'=Landscape
                'print_color_mode': 'color',      # 'monochrome' or 'color'
                'sides': 'one-sided',             # 'one-sided', 'two-sided-long-edge', 'two-sided-short-edge'
                'print_quality': '4',             # '3'=Draft, '4'=Normal, '5'=High
                'page_ranges': '1-5,10-15',       # Page ranges
                'number_up': '1'                  # Pages per sheet
            }

    Usage Examples:
        1. Basic printing:
           print_file(index=1, file_path="/path/to/document.pdf")

        2. Print with options (Windows):
           print_file(index=1, file_path="/path/to/document.pdf", options={
               'dmCopies': 2,
               'dmOrientation': 2,  # Landscape
               'dmColor': 2,        # Color
               'dmPaperSize': 9      # A4
           })

        3. Print with options (Linux/CUPS):
           print_file(index=1, file_path="/path/to/document.pdf", options={
               'copies': '2',
               'orientation_requested': '4',  # Landscape
               'print_color_mode': 'color',
               'media': 'A4'
           })

    Best Practices:
        - Always check printer status before printing
        - Use printer_attrs to determine available options
        - Handle errors gracefully (printer offline, paper out, etc.)
        - Monitor print jobs for completion status
    """

    if _print_file is None:
        response = APIResponse.server_error(f"Unsupported operating system: {platform}")
        return response.to_dict()
    return _print_file(index, file_path, options)


@mcp.tool()
def get_print_jobs(ctx: Context, printer_name: str = None) -> dict:
    """Get print jobs list for a specific printer or all printers

    Args:
        printer_name: Printer name. If None, get jobs from all printers
    """
    if _get_print_jobs is None:
        response = APIResponse.server_error(f"Unsupported operating system: {platform}")
        return response.to_dict()
    return _get_print_jobs(printer_name)


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
def get_print_options_format() -> str:
    """Get print options format for current platform

    Returns:
        str: Platform-specific print options format and examples
    """
    if _get_print_options_format is None:
        return f"Unsupported operating system: {platform}"

    data = _get_print_options_format()
    return json.dumps(data, ensure_ascii=False)


@mcp.prompt()
def print_file_prompt():
    return _print_file_prompt()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
