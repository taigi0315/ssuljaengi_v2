#!/usr/bin/env python3
"""
Test script for enhanced panel generation API endpoints.

This script tests the new configuration and validation endpoints
added for the enhanced panel generation system.
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
WEBTOON_API_BASE = f"{BASE_URL}/webtoon"

def test_endpoint(endpoint: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Test an API endpoint and return the response."""
    url = f"{WEBTOON_API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}...")
            return result
        else:
            print(f"Error: {response.text}")
            return {"error": response.text}
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed to {url}")
        print("Make sure the backend server is running on port 8000")
        return {"error": "connection_failed"}
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {str(e)}")
        return {"error": str(e)}

def main():
    """Test the enhanced panel generation API endpoints."""
    print("🧪 Testing Enhanced Panel Generation API Endpoints")
    print("=" * 60)
    
    # Test 1: Get current panel configuration
    print("\n1. Testing panel configuration retrieval...")
    config_result = test_endpoint("/config/panel-settings")
    
    # Test 2: List supported genres
    print("\n2. Testing genre listing...")
    genres_result = test_endpoint("/config/panel-settings/genres")
    
    # Test 3: Get genre-specific targets
    print("\n3. Testing genre-specific targets...")
    romance_result = test_endpoint("/config/panel-settings/genre/romance")
    
    # Test 4: Validate panel counts
    print("\n4. Testing panel count validation...")
    validation_result = test_endpoint("/config/panel-settings/validate?panel_count=30&genre=romance", "POST")
    
    # Test 5: Try to update configuration (this might fail if validation is strict)
    print("\n5. Testing configuration update...")
    update_data = {
        "panel_count_min": 22,  # Slight increase from default 20
        "single_panel_ratio": 0.65  # Slight increase from default 0.6
    }
    update_result = test_endpoint("/config/panel-settings", "PUT", update_data)
    
    # Test 6: Verify configuration was updated
    if update_result.get("message"):
        print("\n6. Verifying configuration update...")
        updated_config = test_endpoint("/config/panel-settings")
        if updated_config.get("panel_count_settings", {}).get("min") == 22:
            print("✅ Configuration update successful")
        else:
            print("❌ Configuration update may have failed")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    tests = [
        ("Panel Configuration", config_result),
        ("Genre Listing", genres_result),
        ("Genre Targets", romance_result),
        ("Panel Validation", validation_result),
        ("Config Update", update_result),
    ]
    
    passed = 0
    for test_name, result in tests:
        if result and not result.get("error"):
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All enhanced API endpoints are working correctly!")
        return 0
    else:
        print("⚠️  Some endpoints may need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())