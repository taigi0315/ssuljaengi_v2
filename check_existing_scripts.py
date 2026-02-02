#!/usr/bin/env python3
"""
Check existing webtoon scripts to see their structure.
"""

import requests
import json

def check_existing_scripts():
    """Check the structure of existing webtoon scripts."""
    
    try:
        # Get latest scripts
        response = requests.get("http://localhost:8000/webtoon/latest")
        
        if response.status_code == 200:
            scripts = response.json()
            print(f"Found {len(scripts)} existing scripts")
            
            if scripts:
                # Check the first script
                script = scripts[0]
                print(f"\nFirst script structure:")
                print(f"  Script ID: {script.get('script_id', 'N/A')}")
                print(f"  Characters: {len(script.get('characters', []))}")
                print(f"  Has scenes: {'scenes' in script}")
                print(f"  Has panels: {'panels' in script}")
                
                if 'scenes' in script:
                    print(f"  Scenes: {len(script['scenes'])}")
                    if script['scenes']:
                        scene = script['scenes'][0]
                        print(f"    First scene panels: {len(scene.get('panels', []))}")
                
                if 'panels' in script:
                    print(f"  Panels: {len(script['panels'])}")
                
                return True
            else:
                print("No existing scripts found")
                return False
        else:
            print(f"Failed to get scripts: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_existing_scripts()