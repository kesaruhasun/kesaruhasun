#!/usr/bin/env python3
"""
Sync Profile Script
Automates periodic profile updates, regenerating banner SVGs with the profile photo.
"""

import os
import subprocess
import sys
import glob

def main():
    print("Running periodic profile sync for kesaruhasun...")
    
    # Find the profile photo (any common image format in root)
    photo = None
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        matches = glob.glob(ext)
        # Skip SVGs and other generated files
        for m in matches:
            if m not in ('dark.svg', 'light.svg'):
                photo = m
                break
        if photo:
            break
    
    # Re-generate banner SVGs
    cmd = [sys.executable, "generate_banner.py"]
    if photo:
        cmd.append(photo)
        print(f"Using profile photo: {photo}")
    else:
        print("No profile photo found, using placeholder silhouette.")
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
            
    print("Profile sync complete.")

if __name__ == "__main__":
    main()
