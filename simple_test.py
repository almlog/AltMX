import requests

try:
    # Backend test
    response = requests.get("http://localhost:8000/")
    print(f"Backend Status: {response.status_code}")
    
    # Chat test
    response = requests.post("http://localhost:8000/api/chat", 
                           json={"message": "hello", "use_sapporo_dialect": True})
    print(f"Chat API Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response received: {len(response.text)} characters")
    
    # Frontend test
    response = requests.get("http://localhost:5174")
    print(f"Frontend Status: {response.status_code}")
    print(f"Frontend Content Length: {len(response.text)}")
    
except Exception as e:
    print(f"Error: {e}")