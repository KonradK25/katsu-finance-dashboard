#!/usr/bin/env python3
"""
Katsu DCF Engine - Dashboard Launcher

Launches the Streamlit dashboard for interactive DCF analysis.
"""

import subprocess
import sys
import os

def main():
    """Launch the dashboard"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_dir = os.path.join(script_dir, 'src', 'dashboard')
    app_path = os.path.join(dashboard_dir, 'app.py')
    
    print("🚀 Starting Katsu DCF Dashboard...")
    print(f"📍 Dashboard app: {app_path}")
    print("")
    print("Dashboard will open at: http://localhost:8501")
    print("")
    print("Press Ctrl+C to stop the dashboard")
    print("-" * 60)
    
    # Run streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        app_path,
        '--server.port', '8501',
        '--server.address', 'localhost',
        '--server.headless', 'true'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
