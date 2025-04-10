"""
Entry point for the AI Calendar App executable.
This file is used by PyInstaller to create a standalone executable.
"""
import os
import sys
from app import create_app

# Create the Flask application
try:
    app = create_app()
    print("App created successfully.")
    print("Frozen:", getattr(sys, 'frozen', False))
    print("Base dir:", os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd())
    print("Static folder:", app.static_folder)
    print("Template folder:", app.template_folder)  
except Exception as e:
    print(f"Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
# When running as an executable, we need to set the static folder path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_dir = os.path.dirname(sys.executable)
    app.static_folder = os.path.join(base_dir, 'app', 'static')
    app.template_folder = os.path.join(base_dir, 'app', 'templates')

if __name__ == '__main__':
    # Run the application on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=False)
