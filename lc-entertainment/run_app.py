#!/usr/bin/env python3
"""
Simple launcher for the LangChain multi-agent music and map application.
"""

import os
import sys
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Change to the script directory
    os.chdir(script_dir)

    # Set environment variables if needed
    env = os.environ.copy()
    env['PYTHONPATH'] = script_dir

    # Run streamlit
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", "app/frontend/app.py"]
        print(f"Starting LangChain Multi-Agent Application...")
        print(f"Working directory: {script_dir}")
        print(f"Command: {' '.join(cmd)}")
        print("=" * 50)

        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()