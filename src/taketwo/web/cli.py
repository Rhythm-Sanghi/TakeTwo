"""Single local launcher for a built UI and API."""

import argparse
import socket
from pathlib import Path

import uvicorn

from .app import create_app


def main():
    parser = argparse.ArgumentParser(description="TakeTwo — Speech analysis workspace")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--alignment-config", type=Path)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--frontend", type=Path, default=Path("frontend/dist"))
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535.")
    if not args.frontend.is_dir() or not (args.frontend / "index.html").is_file():
        parser.error(
            "Built interface missing. Run npm --prefix frontend run build from the repository."
        )
    try:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", args.port))
    except OSError:
        parser.error(
            f"Port {args.port} is already in use. Stop the existing service or choose --port."
        )
    uvicorn.run(
        create_app(args.workspace, args.alignment_config, frontend=args.frontend),
        host="127.0.0.1",
        port=args.port,
        access_log=False,
    )


if __name__ == "__main__":
    main()
