"""BabelDOC Python Sidecar - JSON-RPC over stdio"""

import asyncio
import sys

from server import JsonRpcServer


def main():
    """主入口"""
    server = JsonRpcServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
