#!/usr/bin/env python3
"""Debug script for GET /vehiculos endpoint"""
import requests
import json

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "123456"

# Login first
print(f"Logging in with {ADMIN_EMAIL}")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
)
print(f"Login Status: {login_response.status_code}")
if login_response.status_code != 200:
    print(f"Login error: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"Token obtained: {token[:20]}...")

# Test GET /vehiculos
headers = {"Authorization": f"Bearer {token}"}
url = f"{BASE_URL}/vehiculos"

print(f"\nTesting GET {url}")
try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    # Try to get JSON response
    try:
        data = response.json()
        print(f"JSON Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Text Response: {response.text[:2000]}")
except Exception as e:
    print(f"Error: {e}")
