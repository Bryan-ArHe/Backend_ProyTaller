#!/usr/bin/env python3
"""Test vehiculos router endpoints"""
import requests

BASE_URL = "http://localhost:8000"

# Test the simple test endpoint first (no auth required)
print("Testing /vehiculos/test endpoint:")
response = requests.get(f"{BASE_URL}/vehiculos/test", timeout=5)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
