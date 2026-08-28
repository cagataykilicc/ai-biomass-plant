"""CLI runner for launching the Digital Twin Web GUI and REST API server.

Usage:
    python -m src.web.run_server --port 8000
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from src.api.server import run_server


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="AI Biomass Plant Digital Twin Web Server (V1.0)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host IP")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--open-browser", action="store_true", help="Automatically open default browser")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}/"
    print(f"\n{'=' * 75}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V1.0")
    print(f"   (Real-Time Interactive Digital Twin Web Platform & REST API)")
    print(f"{'=' * 75}")
    print(f"[*] Serving Digital Twin Dashboard at: {url}")
    print(f"[*] REST API Endpoints active at     : {url}api/status")
    print(f"[*] Press CTRL+C to terminate server.")
    print(f"{'=' * 75}\n")

    if args.open_browser:
        webbrowser.open(url)

    try:
        run_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n[!] Server shutting down cleanly.")


if __name__ == "__main__":
    main()
