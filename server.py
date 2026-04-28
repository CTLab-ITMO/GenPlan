import asyncio
import os

from mcp.server import Server, InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities
from mcp.server.stdio import stdio_server

SERVER_NAME = "GenPlan"
TOOL_NAME = "pipeline"
server = Server(SERVER_NAME)

# Example of initialization
# {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"my-client","version":"0.1"}}}

# Example of request
# {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"pipeline","arguments":{"args":["--text","house"]}}}

@server.list_tools()
async def list_tools():
    current_dir = os.getcwd()
    return [
        Tool(
            name=TOOL_NAME,
            description="Launches the Docker container and returns stdout/stderr",
            inputSchema={
                "type": "object",
                "properties": {
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command line arguments passed to the container",
                        "default": [],
                    },
                    "image": {
                        "type": "string",
                        "description": "Docker image",
                        "default": "egor0ba/gen-plan-api:latest",
                    },
                    "result_folder": {
                        "type": "string",
                        "description": "Result folder",
                        "default": f"{current_dir}/results",
                    },
                },
                "required": ["args"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name != TOOL_NAME:
        raise ValueError(f"Unknown tool: {name}")

    current_dir = os.getcwd()
    image = arguments.get("image", "egor0ba/gen-plan-api:latest")
    result_folder = arguments.get("result_folder", f"{current_dir}/results")
    container_args = arguments.get("args", []) or []

    cmd = ["docker", "run", "--rm", "-v", f"{result_folder}:/GenPlan/results", image]
    cmd += container_args

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()

    stdout = out.decode("utf-8", "ignore")
    stderr = err.decode("utf-8", "ignore")

    if proc.returncode != 0:
        return [
            TextContent(
                type="text",
                text=f"ERROR (exit={proc.returncode})\nCMD: {' '.join(cmd)}\n\nSTDERR:\n{stderr}\n\nSTDOUT:\n{stdout}",
            )
        ]

    return [TextContent(type="text", text=result_folder)]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        initialization_options = InitializationOptions(
            server_name=SERVER_NAME,
            server_version="0.0.1",
            capabilities=ServerCapabilities(),
        )
        await server.run(read_stream, write_stream, initialization_options)


if __name__ == "__main__":
    asyncio.run(main())