#!/usr/bin/env python3
"""
Face Recognition Attendance System
Run this script to start the application
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run main application
from attendance_system import main

if __name__ == "__main__":
    print("Starting Face Recognition Attendance System...")
    print("Make sure your camera is connected.")
    main()