#!/bin/bash
# Test Script for Profile Picture Fetching
# Save this as: test_profile_pics.sh
# Run: bash test_profile_pics.sh

echo "======================================"
echo "Profile Picture Fetch Test"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get auth token (you'll need to update this with your actual token)
TOKEN=$(cat ~/.matcha_token 2>/dev/null || echo "YOUR_TOKEN_HERE")

if [ "$TOKEN" == "YOUR_TOKEN_HERE" ]; then
    echo -e "${YELLOW}⚠️  No token found. Please login first or update TOKEN variable${NC}"
    echo ""
    echo "To save your token, run:"
    echo "  echo 'YOUR_ACCESS_TOKEN' > ~/.matcha_token"
    echo ""
fi

BASE_URL="http://localhost:5000"

echo "Testing Backend Connectivity..."
echo "================================"
echo ""

# Test 1: Check if backend is running
echo "1. Testing backend health..."
if curl -s -f "${BASE_URL}/api/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not responding${NC}"
    echo "  Please start backend: cd matcha_backend && python3 app.py"
    exit 1
fi
echo ""

# Test 2: Check CORS headers
echo "2. Testing CORS headers..."
CORS_HEADERS=$(curl -s -I -X OPTIONS \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: GET" \
    "${BASE_URL}/api/profile/me" 2>&1)

if echo "$CORS_HEADERS" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✓ CORS headers present${NC}"
else
    echo -e "${RED}✗ CORS headers missing${NC}"
    echo "  Backend needs CORS configuration update"
fi
echo ""

# Test 3: Test profile API endpoint
echo "3. Testing profile API endpoint..."
if [ "$TOKEN" != "YOUR_TOKEN_HERE" ]; then
    PROFILE_RESPONSE=$(curl -s -X GET \
        -H "Authorization: Bearer ${TOKEN}" \
        "${BASE_URL}/api/profile/me")
    
    if echo "$PROFILE_RESPONSE" | grep -q "error"; then
        echo -e "${RED}✗ Profile API error${NC}"
        echo "  Response: $PROFILE_RESPONSE"
    else
        echo -e "${GREEN}✓ Profile API working${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipped (no token)${NC}"
fi
echo ""

# Test 4: Test profile picture endpoint
echo "4. Testing profile picture endpoint..."
if [ "$TOKEN" != "YOUR_TOKEN_HERE" ]; then
    PIC_RESPONSE=$(curl -s -X GET \
        -H "Authorization: Bearer ${TOKEN}" \
        "${BASE_URL}/api/profile/get_profile_pic/me")
    
    if echo "$PIC_RESPONSE" | grep -q '"result"'; then
        PIC_PATH=$(echo "$PIC_RESPONSE" | grep -o '"/static[^"]*"' | tr -d '"')
        echo -e "${GREEN}✓ Profile picture API working${NC}"
        echo "  Picture path: ${PIC_PATH}"
        
        # Test 5: Check if static file is accessible
        echo ""
        echo "5. Testing static file access..."
        if [ -n "$PIC_PATH" ]; then
            STATIC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${PIC_PATH}")
            if [ "$STATIC_RESPONSE" == "200" ]; then
                echo -e "${GREEN}✓ Static file accessible${NC}"
            elif [ "$STATIC_RESPONSE" == "404" ]; then
                echo -e "${RED}✗ Static file not found (404)${NC}"
                echo "  File may not exist at: ${BASE_URL}${PIC_PATH}"
            else
                echo -e "${YELLOW}⚠️  Unexpected response: ${STATIC_RESPONSE}${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  No picture path found${NC}"
        fi
    else
        echo -e "${RED}✗ Profile picture API error${NC}"
        echo "  Response: $PIC_RESPONSE"
    fi
else
    echo -e "${YELLOW}⚠️  Skipped (no token)${NC}"
fi
echo ""

# Test 6: Check static directory
echo "6. Checking static directory..."
if [ -d "matcha_backend/static/profiles" ]; then
    PROFILE_COUNT=$(find matcha_backend/static/profiles -type f 2>/dev/null | wc -l)
    echo -e "${GREEN}✓ Static directory exists${NC}"
    echo "  Found ${PROFILE_COUNT} files"
    
    # Show recent uploads
    echo ""
    echo "  Recent uploads:"
    find matcha_backend/static/profiles -type f -printf "  %p (modified: %TY-%Tm-%Td %TH:%TM)\n" 2>/dev/null | head -5
else
    echo -e "${RED}✗ Static directory not found${NC}"
    echo "  Expected: matcha_backend/static/profiles"
fi
echo ""

# Summary
echo "======================================"
echo "Summary & Next Steps"
echo "======================================"
echo ""
echo "If you see CORS errors in browser console:"
echo "  1. Restart Flask backend (as root):"
echo "     ${YELLOW}sudo su${NC}"
echo "     ${YELLOW}pkill -f 'python.*app.py'${NC}"
echo "     ${YELLOW}cd /home/khaoula/matcha_1/matcha_backend${NC}"
echo "     ${YELLOW}python3 app.py${NC}"
echo ""
echo "  2. Clear browser cache:"
echo "     ${YELLOW}Ctrl+Shift+R${NC} (hard refresh)"
echo ""
echo "  3. Check browser console (F12) for errors"
echo ""
echo "If static files return 404:"
echo "  1. Verify image_handler.py has correct path (profile_picture not pofile_picture)"
echo "  2. Upload a new photo to test"
echo "  3. Check file permissions in static/profiles directory"
echo ""

