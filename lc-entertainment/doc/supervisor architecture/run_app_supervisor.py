#!/usr/bin/env python3
"""
Supervisor Agent 启动脚本
使用智能路由的多Agent系统
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

    # Run streamlit with supervisor frontend
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", "app/frontend/app_supervisor.py"]
        print(f"Starting Supervisor Agent System...")
        print(f"Working directory: {script_dir}")
        print(f"Command: {' '.join(cmd)}")
        print("=" * 80)
        print("🤖 智能多Agent系统")
        print("✨ 特性:")
        print("  - 自动意图识别和Agent路由")
        print("  - 完整的任务执行追踪")
        print("  - 实时性能监控")
        print("  - 可观测性数据导出")
        print("=" * 80)

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
