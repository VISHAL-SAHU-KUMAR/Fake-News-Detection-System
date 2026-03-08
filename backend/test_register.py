import requests
import json
import random

url = 'http://127.0.0.1:8000/auth/register'
data = {
    'name': 'Test User Python',
    'email': f'test_{random.randint(1000, 9999)}@example.com',
    'password': 'Password123!'
}

try:
    response = requests.post(url, json=data)
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'Error: {e}')
