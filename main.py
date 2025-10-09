from sys import platform
from mcp.server.fastmcp import FastMCP, Context

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
    from local_printer.cups import print_file_prompt as _print_file_prompt
else:
    _get_printer_list = None
    _get_printer_status = None
    _get_printer_attrs = None


# Create MCP server
mcp = FastMCP("PrinterAIMCP",
              website_url="https://github.com/NullYing/printer-ai-mcp")


@mcp.tool()
def get_printer_list() -> dict:
    """Get system printer list"""
    if _get_printer_list is None:
        return {
            "code": 500,
            "msg": f"Unsupported operating system: {platform}",
            "data": {"printers": [], "count": 0}
        }
    
    data_list = _get_printer_list()
    return data_list


@mcp.tool()
def printer_status(ctx: Context, index: int = None) -> dict:
    """Get printer status by index
    
    Args:
        index: Printer index (1-based). If None, returns the default printer status
    """
    if _get_printer_status is None:
        return {
            "code": 500,
            "msg": f"Unsupported operating system: {platform}",
            "data": {}
        }
    
    return _get_printer_status(index)


@mcp.tool()
def printer_attrs(ctx: Context, index: int = None) -> dict:
    if _get_printer_attrs is None:
        return {
            "code": 500,
            "msg": f"Unsupported operating system: {platform}",
            "data": {}
        }
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
        return {
            "code": 500,
            "msg": f"Unsupported operating system: {platform}",
            "data": {}
        }
    return _print_file(index, file_path, options)


@mcp.prompt()
def print_file_prompt():
  return _print_file_prompt()


if __name__ == '__main__':
    mcp.run(transport="streamable-http")
