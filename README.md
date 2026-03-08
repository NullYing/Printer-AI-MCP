# Printer AI MCP

[中文文档](README_CN.md)

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

**Parameters:**
- `index`: Printer index (1-based). If `None`, uses the default printer
- `file_path`: Path to the file to print
- `options`: Print options dict (optional), format differs by platform:

<details>
<summary>🪟 <b>Windows Options</b> — <a href="https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-devmodew">DEVMODE Documentation</a></summary>

Windows uses [Device Mode (DEVMODE)](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-devmodew) parameters with `dm` prefix:

```json
{
    "dmCopies": 2,
    "dmOrientation": 1,
    "dmColor": 2,
    "dmPaperSize": 9,
    "dmDuplex": 1,
    "dmDefaultSource": 7,
    "dmMediaType": 0,
    "dmPrintQuality": -4,
    "dmCollate": 1
}
```

| Option | Type | Description |
|--------|------|-------------|
| `dmCopies` | int | Number of copies |
| `dmOrientation` | int | `1` = Portrait, `2` = Landscape |
| `dmColor` | int | `1` = Monochrome, `2` = Color |
| `dmPaperSize` | int | Paper size constant (`1` = Letter, `5` = Legal, `8` = A3, `9` = A4, `11` = A5) |
| `dmDuplex` | int | `1` = Simplex, `2` = Long Edge, `3` = Short Edge |
| `dmDefaultSource` | int | Paper source / bin |
| `dmMediaType` | int | Media type |
| `dmPrintQuality` | int | Print quality (`-4` = Default, positive values = DPI) |
| `dmCollate` | int | `1` = Collate, `0` = No collate |

</details>

<details>
<summary>🐧🍎 <b>Linux / macOS Options</b> — CUPS/IPP Format</summary>

Linux and macOS use [CUPS](https://www.cups.org/doc/options.html) with IPP standard options:

```json
{
    "copies": "2",
    "media": "A4",
    "orientation_requested": "3",
    "print_color_mode": "color",
    "sides": "one-sided",
    "print_quality": "4",
    "page_ranges": "1-5,10-15",
    "number_up": "1"
}
```

| Option | Type | Description |
|--------|------|-------------|
| `copies` | str | Number of copies |
| `media` | str | Paper size (e.g., `A4`, `Letter`, `Legal`) |
| `orientation_requested` | str | `3` = Portrait, `4` = Landscape |
| `print_color_mode` | str | `monochrome` or `color` |
| `sides` | str | `one-sided`, `two-sided-long-edge`, `two-sided-short-edge` |
| `print_quality` | str | `3` = Draft, `4` = Normal, `5` = High |
| `page_ranges` | str | Page ranges (e.g., `1-5,10-15`) |
| `number_up` | str | Pages per sheet |

</details>

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
