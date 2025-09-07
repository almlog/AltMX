"""
AltMX MVP動作テスト
TDDの原則に従い、実際の動作確認を行う
"""

import requests
import json
import time
from datetime import datetime


def test_backend_api():
    """バックエンドAPI動作テスト"""
    print("=== Backend API Tests ===")
    
    try:
        # Root endpoint test
        response = requests.get("http://localhost:8000/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Message: {response.json()['message']}")
        
        # Chat API test
        chat_data = {
            "message": "こんにちは",
            "use_sapporo_dialect": True
        }
        response = requests.post("http://localhost:8000/api/chat", 
                               json=chat_data)
        print(f"✅ Chat API: {response.status_code}")
        data = response.json()
        print(f"   Response: {data['response']}")
        print(f"   Dialect: {data['dialect_applied']}")
        print(f"   Time: {data['thinking_time_ms']}ms")
        
        # Car animation API test
        response = requests.get("http://localhost:8000/api/car-animation")
        print(f"✅ Car Animation API: {response.status_code}")
        car_data = response.json()
        print(f"   Car: {car_data['car_emoji']} Blinking: {car_data['lights_blinking']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend API Error: {e}")
        return False


def test_frontend_accessibility():
    """フロントエンド接続テスト"""
    print("\n=== Frontend Accessibility Tests ===")
    
    try:
        response = requests.get("http://localhost:5174")
        print(f"✅ Frontend accessible: {response.status_code}")
        
        # Check if it's not empty/error page
        if len(response.content) < 100:
            print("❌ Frontend returns very little content")
            return False
            
        # Check for common error patterns
        content = response.text.lower()
        if "error" in content or "404" in content:
            print("❌ Frontend shows error content")
            return False
            
        print("✅ Frontend content looks healthy")
        return True
        
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
        return False


def test_cors_integration():
    """CORS統合テスト"""
    print("\n=== CORS Integration Tests ===")
    
    try:
        # Simulate frontend to backend call with CORS headers
        headers = {
            'Origin': 'http://localhost:5174',
            'Content-Type': 'application/json'
        }
        
        chat_data = {
            "message": "CORS テスト",
            "use_sapporo_dialect": True
        }
        
        response = requests.post("http://localhost:8000/api/chat",
                               json=chat_data, headers=headers)
        
        print(f"✅ CORS Request: {response.status_code}")
        
        # Check CORS headers
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f"✅ CORS Header present: {cors_header}")
            return True
        else:
            print("❌ Missing CORS headers")
            return False
            
    except Exception as e:
        print(f"❌ CORS Error: {e}")
        return False


def main():
    """メインテスト実行"""
    print(f"AltMX MVP Integration Test - {datetime.now()}")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(("Backend API", test_backend_api()))
    results.append(("Frontend", test_frontend_accessibility()))
    results.append(("CORS Integration", test_cors_integration()))
    
    # Results summary
    print("\n" + "=" * 50)
    print("=== Test Results ===")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\n🔥 MVP is NOT ready for production!")
        print("Fix failing tests before claiming completion.")
    else:
        print("\n🎉 MVP basic functionality confirmed!")


if __name__ == "__main__":
    main()