# Printer AI MCP

一个跨平台的打印机AI MCP服务器，支持Windows、macOS和Linux系统，提供打印机管理、状态查询和文件打印功能。

## 功能特性

- 🌍 **跨平台支持**: Windows、macOS、Linux
- 🖨️ **打印机管理**: 获取打印机列表、状态查询
- 📄 **文件打印**: 支持多种文件格式打印
- 🔧 **打印机属性**: 获取详细打印机配置信息
- 📊 **任务管理**: 打印任务状态查询和取消
- 🚀 **MCP协议**: 基于FastMCP构建，支持AI助手集成

## 系统要求

- Python 3.10+
- Windows: 建议Windows 10以上
- macOS/Linux: CUPS支持

## 安装

### 使用uv安装

```bash
# 克隆项目
git clone https://github.com/NullYing/printer-ai-mcp.git
cd printer-ai-mcp

# 安装依赖
uv sync
```

## 使用方法

### 启动MCP服务器

```bash
python main.py
```

### 可用的MCP工具

#### 1. 获取打印机列表
```python
get_printer_list() -> dict
```
返回系统中所有可用的打印机列表。

#### 2. 获取打印机状态
```python
printer_status(index: int = None) -> dict
```
获取指定打印机的状态信息。如果不指定index，则返回默认打印机状态。

#### 3. 获取打印机属性
```python
printer_attrs(index: int = None) -> dict
```
获取打印机的详细配置属性（仅macOS/Linux支持）。

#### 4. 打印文件
```python
print_file(index: int = None, file_path: str = None, options: dict = None) -> dict
```
使用指定打印机打印文件。支持自定义打印选项。

### API响应格式

所有API都返回统一格式的响应：

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        // 具体数据内容
    }
}
```

## 配置

### MCP配置示例

在你的MCP配置文件中添加：

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

## 开发

### 项目结构

```
printer-ai-mcp/
├── main.py                 # MCP服务器主文件
├── local_printer/          # 本地打印机模块
│   ├── __init__.py
│   ├── cups.py            # macOS/Linux CUPS支持
│   └── windows.py         # Windows打印机支持
├── network_printer/       # 网络打印机模块（待开发）
│   └── __init__.py
├── pyproject.toml         # 项目配置
└── README.md              # 项目说明
```

### 贡献

我们欢迎社区贡献！您可以通过以下方式帮助我们：

- ⭐ **给项目点星** 表示您的支持，帮助其他人发现这个项目
- 🐛 **报告Bug** 通过提交详细的issue来报告问题
- 💡 **建议新功能** 或改进，通过GitHub issues提出
- 🔧 **提交Pull Request** 修复bug或添加新功能
- 📖 **改进文档** 帮助其他用户更好地理解项目
- 🧪 **在不同平台测试** 并报告兼容性问题

您的贡献让这个项目变得更好。感谢您的支持！

## 许可证

MIT License

## 相关链接

- [项目主页](https://github.com/NullYing/printer-ai-mcp)
- [MCP协议文档](https://modelcontextprotocol.io/)
- [CUPS文档](https://www.cups.org/)
