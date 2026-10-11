"""Single local launcher for a built UI and API."""

import argparse
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
    uvicorn.run(
        create_app(args.workspace, args.alignment_config, frontend=args.frontend),
        host="127.0.0.1",
        port=args.port,
        access_log=False,
    )


if __name__ == "__main__":
    main()
