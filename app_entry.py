"""
Entry point for the AI Calendar App executable.
This file is used by PyInstaller to create a standalone executable.
"""
import os
import sys
from app import create_app

# Create the Flask application
app = create_app()

# When running as an executable, we need to set the static folder path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_dir = os.path.dirname(sys.executable)
    app.static_folder = os.path.join(base_dir, 'app', 'static')
    app.template_folder = os.path.join(base_dir, 'app', 'templates')

if __name__ == '__main__':
    # Run the application on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=False)
