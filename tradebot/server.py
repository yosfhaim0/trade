import argparse
import functools
import http.server
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve bot reports")
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Directory with status.json and trades.csv",
    )
    parser.add_argument("--port", type=int, default=8000, help="Port to serve")
    args = parser.parse_args()

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(args.reports_dir)
    )
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler) as httpd:
        print(f"Serving {args.reports_dir} on port {args.port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
