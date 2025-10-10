# Printer AI MCP

A cross-platform printer AI MCP server that supports Windows, macOS, and Linux systems, providing printer management, status queries, and file printing capabilities.

## Features

- 🌍 **Cross-platform Support**: Windows, macOS, Linux
- 🖨️ **Printer Management**: Get printer list, status queries
- 📄 **File Printing**: Support multiple file format printing
- 🔧 **Printer Attributes**: Get detailed printer configuration information
- 📊 **Task Management**: Print job status queries and cancellation
- 🚀 **MCP Protocol**: Built on FastMCP, supports AI assistant integration

## System Requirements

- Python 3.10+
- Windows: Recommended Windows 10 or above
- macOS/Linux: CUPS support

## Installation

### Using uv Installation

```bash
# Clone the project
git clone https://github.com/NullYing/printer-ai-mcp.git
cd printer-ai-mcp

# Install dependencies
uv sync
```

## Usage

### Start MCP Server

```bash
python main.py
```

### Available MCP Tools

#### 1. Get Printer List

```python
get_printer_list() -> dict
```

Returns a list of all available printers in the system.

#### 2. Get Printer Status

```python
printer_status(index: int = None) -> dict
```

Gets the status information of the specified printer. If no index is specified, returns the default printer status.

#### 3. Get Printer Attributes

```python
printer_attrs(index: int = None) -> dict
```

Gets detailed configuration attributes of the printer (macOS/Linux only).

#### 4. Print File

```python
print_file(index: int = None, file_path: str = None, options: dict = None) -> dict
```

Prints files using the specified printer. Supports custom print options.

### API Response Format

All APIs return responses in a unified format:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    // Specific data content
  }
}
```

## Configuration

### MCP Configuration Example

Add to your MCP configuration file:

```json
{
  "mcpServers": {
    "printerAIMcp": {
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {}
    }
  }
}
```

## Development

### Project Structure

```
printer-ai-mcp/
├── main.py                 # MCP server main file
├── local_printer/          # Local printer module
│   ├── __init__.py
│   ├── cups.py            # macOS/Linux CUPS support
│   └── windows.py         # Windows printer support
├── network_printer/       # Network printer module (to be developed)
│   └── __init__.py
├── pyproject.toml         # Project configuration
└── README.md              # Project documentation
```

### Contributing

We welcome contributions from the community! Here are several ways you can help:

- ⭐ **Star this repository** to show your support and help others discover this project
- 🐛 **Report bugs** by opening an issue with detailed information about the problem
- 💡 **Suggest new features** or improvements through GitHub issues
- 🔧 **Submit pull requests** to fix bugs or add new functionality
- 📖 **Improve documentation** to help other users understand the project better
- 🧪 **Test on different platforms** and report compatibility issues

Your contributions help make this project better for everyone. Thank you for your support!

## License

MIT License

## Related Links

- [Project Homepage](https://github.com/NullYing/printer-ai-mcp)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [CUPS Documentation](https://www.cups.org/)
