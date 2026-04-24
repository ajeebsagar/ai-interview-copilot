#!/bin/bash
# LockedIn AI - API Testing Script
# Tests all endpoints end-to-end

API_URL="http://localhost:8000"
API_KEY="MySecretKey12345!@#$%"

echo "=========================================="
echo "LockedIn AI - API Endpoint Testing"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "-------------------"
curl -s "$API_URL/api/v1/health" | python -m json.tool
echo ""
echo ""

# Test 2: Root Endpoint
echo "Test 2: Root Endpoint"
echo "-------------------"
curl -s "$API_URL/" | python -m json.tool
echo ""
echo ""

# Test 3: Chat Completion (Simple)
echo "Test 3: Chat Completion - Simple Question"
echo "-------------------"
curl -s -X POST "$API_URL/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is binary search? Answer in one sentence."}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }' | python -m json.tool
echo ""
echo ""

# Test 4: Chat Completion with Session
echo "Test 4: Chat Completion - With Session Context"
echo "-------------------"
SESSION_ID="test-session-$(date +%s)"
curl -s -X POST "$API_URL/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"messages\": [
      {\"role\": \"user\", \"content\": \"My name is Alice\"}
    ],
    \"session_id\": \"$SESSION_ID\",
    \"max_tokens\": 50
  }" | python -m json.tool
echo ""
echo ""

# Test 5: Follow-up in same session
echo "Test 5: Chat Completion - Follow-up (Context Test)"
echo "-------------------"
curl -s -X POST "$API_URL/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"messages\": [
      {\"role\": \"user\", \"content\": \"What name did I just tell you?\"}
    ],
    \"session_id\": \"$SESSION_ID\",
    \"max_tokens\": 50
  }" | python -m json.tool
echo ""
echo ""

# Test 6: Create Duo Session
echo "Test 6: Create Duo Mode Session"
echo "-------------------"
DUO_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "user_id": "test-user-1",
    "session_name": "Test Session"
  }')
echo "$DUO_RESPONSE" | python -m json.tool
DUO_SESSION_ID=$(echo "$DUO_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null)
DUO_INVITE_CODE=$(echo "$DUO_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['invite_code'])" 2>/dev/null)
echo ""
echo ""

# Test 7: Get Session Info
if [ ! -z "$DUO_SESSION_ID" ]; then
  echo "Test 7: Get Duo Session Info"
  echo "-------------------"
  curl -s "$API_URL/api/v1/sessions/$DUO_SESSION_ID" \
    -H "X-API-Key: $API_KEY" | python -m json.tool
  echo ""
  echo ""

  # Test 8: Join Session
  echo "Test 8: Join Duo Session"
  echo "-------------------"
  curl -s -X POST "$API_URL/api/v1/sessions/$DUO_SESSION_ID/join" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "{
      \"invite_code\": \"$DUO_INVITE_CODE\",
      \"user_id\": \"test-user-2\"
    }" | python -m json.tool
  echo ""
  echo ""
fi

# Test 9: Audio Transcription (will be mock)
echo "Test 9: Audio Transcription (Mock Mode)"
echo "-------------------"
echo "Creating dummy audio file..."
echo "test audio data" > /tmp/test_audio.wav
curl -s -X POST "$API_URL/api/v1/audio/transcribe" \
  -H "X-API-Key: $API_KEY" \
  -F "audio=@/tmp/test_audio.wav" \
  -F "language=en" | python -m json.tool
echo ""
echo ""

echo "=========================================="
echo "API Testing Complete!"
echo "=========================================="
