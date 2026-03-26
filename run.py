# SmartRoute Pro — Application entry point
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

import argparse
import subprocess
import sys
from pathlib import Path


def run_api():
    """Start the FastAPI backend server."""
    import uvicorn
    from app.config import config

    uvicorn.run(
        "app.api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
    )


def run_dashboard():
    """Start the Streamlit dashboard."""
    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.headless=true",
    ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SmartRoute Pro")
    parser.add_argument(
        "mode",
        choices=["api", "dashboard", "both"],
        default="dashboard",
        nargs="?",
        help="Run mode: 'api' for FastAPI, 'dashboard' for Streamlit, 'both' for both",
    )
    args = parser.parse_args()

    if args.mode == "api":
        run_api()
    elif args.mode == "dashboard":
        run_dashboard()
    elif args.mode == "both":
        import threading
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        run_dashboard()
