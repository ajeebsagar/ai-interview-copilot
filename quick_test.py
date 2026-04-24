"""
Quick API Test Script for LockedIn AI
Tests backend API endpoints using requests library
"""
import requests
import json
from datetime import datetime


API_URL = "http://localhost:8000"
API_KEY = "MySecretKey12345!@#$%"
HEADERS = {"X-API-Key": API_KEY}

test_results = []


def test(name, condition, message=""):
    """Log test result."""
    status = "✅ PASS" if condition else "❌ FAIL"
    result = {
        "name": name,
        "passed": condition,
        "message": message
    }
    test_results.append(result)
    print(f"{status} - {name}")
    if message:
        print(f"   {message}")
    return condition


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("LOCKEDIN AI - QUICK API TEST")
    print("="*70 + "\n")

    passed = 0
    failed = 0

    # Test 1: Check if server is running
    print("Test 1: Backend Server Status")
    try:
        response = requests.get(f"{API_URL}/api/v1/health", timeout=5)
        if test("Server Health Check", response.status_code == 200,
                f"Status code: {response.status_code}"):
            passed += 1
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            failed += 1
    except Exception as e:
        test("Server Health Check", False, f"Error: {e}")
        failed += 1
        print("\n❌ Backend server is not running!")
        print("Please start it with:")
        print("  cd backend")
        print("  venv\\Scripts\\activate.bat")
        print("  python -m uvicorn src.main:app --reload")
        return

    print()

    # Test 2: Root endpoint
    print("Test 2: Root Endpoint")
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if test("Root Endpoint", response.status_code == 200):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        test("Root Endpoint", False, f"Error: {e}")
        failed += 1

    print()

    # Test 3: Authentication - No key
    print("Test 3: Authentication (No Key)")
    try:
        response = requests.post(
            f"{API_URL}/api/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "test"}]},
            timeout=10
        )
        if test("Auth Rejects No Key", response.status_code == 403,
                f"Expected 403, got {response.status_code}"):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        test("Auth Rejects No Key", False, f"Error: {e}")
        failed += 1

    print()

    # Test 4: Authentication - Wrong key
    print("Test 4: Authentication (Wrong Key)")
    try:
        response = requests.post(
            f"{API_URL}/api/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "test"}]},
            headers={"X-API-Key": "wrong-key"},
            timeout=10
        )
        if test("Auth Rejects Wrong Key", response.status_code == 403,
                f"Expected 403, got {response.status_code}"):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        test("Auth Rejects Wrong Key", False, f"Error: {e}")
        failed += 1

    print()

    # Test 5: Chat completion (simple)
    print("Test 5: Chat Completion (Simple)")
    try:
        response = requests.post(
            f"{API_URL}/api/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "What is 2+2? Answer with just the number."}
                ],
                "max_tokens": 50
            },
            headers=HEADERS,
            timeout=30
        )
        if test("Chat Completion", response.status_code == 200,
                f"Status: {response.status_code}"):
            passed += 1
            data = response.json()
            print(f"   AI Response: {data.get('content', '')[:100]}")
        else:
            failed += 1
            print(f"   Error: {response.text}")
    except Exception as e:
        test("Chat Completion", False, f"Error: {e}")
        failed += 1

    print()

    # Test 6: Chat with context
    print("Test 6: Chat with Context (Session Memory)")
    session_id = f"test-{int(datetime.now().timestamp())}"
    try:
        # First message
        response1 = requests.post(
            f"{API_URL}/api/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "My name is Alice."}],
                "session_id": session_id,
                "max_tokens": 50
            },
            headers=HEADERS,
            timeout=30
        )

        if response1.status_code == 200:
            # Second message (test context)
            response2 = requests.post(
                f"{API_URL}/api/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": "What's my name?"}],
                    "session_id": session_id,
                    "max_tokens": 50
                },
                headers=HEADERS,
                timeout=30
            )

            if response2.status_code == 200:
                data2 = response2.json()
                content = data2.get('content', '').lower()
                remembered = 'alice' in content

                if test("Context Memory", remembered,
                        f"AI {'remembered' if remembered else 'forgot'} the name"):
                    passed += 1
                    print(f"   AI Response: {data2.get('content', '')}")
                else:
                    failed += 1
            else:
                test("Context Memory", False, f"Second request failed: {response2.status_code}")
                failed += 1
        else:
            test("Context Memory", False, f"First request failed: {response1.status_code}")
            failed += 1
    except Exception as e:
        test("Context Memory", False, f"Error: {e}")
        failed += 1

    print()

    # Test 7: Create Duo session
    print("Test 7: Duo Mode - Create Session")
    try:
        response = requests.post(
            f"{API_URL}/api/v1/sessions",
            json={"user_id": "test-user-1", "session_name": "Test Session"},
            headers=HEADERS,
            timeout=10
        )

        if test("Session Create", response.status_code == 200,
                f"Status: {response.status_code}"):
            passed += 1
            data = response.json()
            session_id = data.get('session_id')
            invite_code = data.get('invite_code')
            print(f"   Session ID: {session_id}")
            print(f"   Invite Code: {invite_code}")

            # Test 8: Join session
            print("\nTest 8: Duo Mode - Join Session")
            response2 = requests.post(
                f"{API_URL}/api/v1/sessions/{session_id}/join",
                json={"invite_code": invite_code, "user_id": "test-user-2"},
                headers=HEADERS,
                timeout=10
            )

            if test("Session Join", response2.status_code == 200,
                    f"Status: {response2.status_code}"):
                passed += 1
            else:
                failed += 1

            # Test 9: Get session info
            print("\nTest 9: Duo Mode - Get Session Info")
            response3 = requests.get(
                f"{API_URL}/api/v1/sessions/{session_id}",
                headers=HEADERS,
                timeout=10
            )

            if test("Session Info", response3.status_code == 200,
                    f"Status: {response3.status_code}"):
                passed += 1
                info = response3.json()
                print(f"   Participants: {info.get('participants', [])}")
            else:
                failed += 1
        else:
            failed += 1
            print(f"   Error: {response.text}")
            # Skip dependent tests
            test("Session Join", False, "Skipped (session creation failed)")
            test("Session Info", False, "Skipped (session creation failed)")
            failed += 2
    except Exception as e:
        test("Session Create", False, f"Error: {e}")
        test("Session Join", False, "Skipped")
        test("Session Info", False, "Skipped")
        failed += 3

    print()

    # Test 10: Audio transcription
    print("Test 10: Audio Transcription (Mock Mode)")
    try:
        files = {"audio": ("test.wav", b"fake audio data", "audio/wav")}
        data = {"language": "en"}

        response = requests.post(
            f"{API_URL}/api/v1/audio/transcribe",
            files=files,
            data=data,
            headers=HEADERS,
            timeout=10
        )

        if test("Audio Transcription", response.status_code == 200,
                f"Status: {response.status_code}"):
            passed += 1
            result = response.json()
            print(f"   Transcription: {result.get('transcription', '')}")
        else:
            failed += 1
            print(f"   Error: {response.text}")
    except Exception as e:
        test("Audio Transcription", False, f"Error: {e}")
        failed += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    total = passed + failed
    print(f"Total Tests:  {total}")
    print(f"✅ Passed:    {passed}")
    print(f"❌ Failed:    {failed}")

    if total > 0:
        success_rate = (passed / total) * 100
        print(f"Success Rate: {success_rate:.1f}%")

    # Save results
    with open("quick_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{success_rate:.1f}%" if total > 0 else "0%",
            "tests": test_results
        }, f, indent=2)

    print(f"\nResults saved to: quick_test_results.json")
    print("="*70 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
