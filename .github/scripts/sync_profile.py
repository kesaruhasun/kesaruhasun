#!/usr/bin/env python3
"""
Sync Profile Script
Automates periodic profile updates, regenerating banner SVGs and updating README.md cleanly.
Can be expanded to fetch live JSON datasets or APIs.
"""

import os
import subprocess
import sys

def main():
    print("Running periodic profile sync for kesaruhasun...")
    
    # 1. Re-generate banner SVGs
    if os.path.exists("generate_banner.py"):
        res = subprocess.run([sys.executable, "generate_banner.py"], capture_output=True, text=True)
        print(res.stdout)
        if res.stderr:
            print(res.stderr, file=sys.stderr)
            
    print("Profile sync complete.")

if __name__ == "__main__":
    main()
