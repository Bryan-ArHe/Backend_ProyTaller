#!/usr/bin/env python3
"""Simple test to check if server is running"""
import requests

url = "http://localhost:8000/docs"
try:
    response = requests.get(url, timeout=2)
    print(f"Server status: {response.status_code}")
except Exception as e:
    print(f"Server not running: {e}")
