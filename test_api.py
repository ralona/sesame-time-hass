#!/usr/bin/env python3
"""Test script for Sesame Time API."""

import asyncio
import aiohttp
import logging
import sys
import os
from dotenv import load_dotenv

# Add the custom_components path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'sesame_time'))

from api import SesameTimeAPI
from const import DEFAULT_TIMEOUT, USER_AGENT

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_api():
    """Test the Sesame Time API."""
    
    # Load environment variables (.env.local takes precedence)
    load_dotenv()
    load_dotenv(".env.local")
    
    # Get credentials from environment variables
    REGION = os.getenv("SESAME_REGION", "eu1")
    EMAIL = os.getenv("SESAME_EMAIL")
    PASSWORD = os.getenv("SESAME_PASSWORD")
    
    if not EMAIL or not PASSWORD:
        print("❌ Error: Missing credentials!")
        print("Please create a .env file with:")
        print("SESAME_REGION=eu1")
        print("SESAME_EMAIL=your-email@example.com")
        print("SESAME_PASSWORD=your-password")
        return
    
    print(f"🔐 Testing Sesame Time API")
    print(f"Region: {REGION}")
    print(f"Email: {EMAIL}")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        api = SesameTimeAPI(session, REGION)
        
        try:
            # Test 1: Login
            print("\n📝 Test 1: Login...")
            login_result = await api.login(EMAIL, PASSWORD)
            if login_result.get("success"):
                print(f"✅ Login successful!")
                print(f"   Token: {login_result.get('token')[:20]}...")
            else:
                print(f"❌ Login failed: {login_result.get('error')}")
                return
            
            # Test 2: Get user info
            print("\n👤 Test 2: Get user info...")
            user_result = await api.get_me()
            if user_result.get("success"):
                print(f"✅ User info retrieved!")
                print(f"   Employee: {user_result.get('employee_name')}")
                print(f"   Company: {user_result.get('company_name')}")
                print(f"   Employee ID: {user_result.get('employee_id')}")
                print(f"   Company ID: {user_result.get('company_id')}")
                print(f"   Work status: {user_result.get('work_status')}")
            else:
                print(f"❌ Get user info failed: {user_result.get('error')}")
                return
            
            # Test 3: Get status
            print("\n📊 Test 3: Get current status...")
            status_result = await api.get_status()
            if status_result.get("success"):
                print(f"✅ Status retrieved!")
                print(f"   Checked in: {status_result.get('is_checked_in')}")
                print(f"   Last check-in: {status_result.get('last_check_in')}")
                print(f"   Last check-out: {status_result.get('last_check_out')}")
            else:
                print(f"❌ Get status failed: {status_result.get('error')}")
            
            # Test 4: Check-in/out with coordinates
            print("\n🚪 Test 4: Check-in/out with coordinates test...")
            
            # Test coordinates (example coordinates - replace with your own)
            test_latitude = 40.4168
            test_longitude = -3.7038
            
            if status_result.get("is_checked_in"):
                print(f"Currently checked in, performing check-out with coordinates...")
                print(f"  Latitude: {test_latitude}")
                print(f"  Longitude: {test_longitude}")
                result = await api.check_out(latitude=test_latitude, longitude=test_longitude)
                action = "check-out"
            else:
                print(f"Currently checked out, performing check-in with coordinates...")
                print(f"  Latitude: {test_latitude}")
                print(f"  Longitude: {test_longitude}")
                result = await api.check_in(latitude=test_latitude, longitude=test_longitude)
                action = "check-in"
            
            if result.get("success"):
                print(f"✅ {action} with coordinates successful!")
            else:
                print(f"❌ {action} with coordinates failed: {result.get('error')}")
            
            print("\n🎉 ALL API TESTS COMPLETED!")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("Sesame Time API Test Script")
    print("=" * 50)
    print("⚠️  Create a .env file with your credentials!")
    print("=" * 50)
    asyncio.run(test_api())
