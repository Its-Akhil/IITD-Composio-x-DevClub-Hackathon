#!/usr/bin/env python3
"""
Test external API connections
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.services.llm_service import LLMService
from app.services.sheets_service import SheetsService
from app.services.slack_service import SlackService
from app.services.wordpress_service import WordPressService


async def test_gemini():
    """Test Gemini API"""
    print("\\n🔍 Testing Gemini API...")
    try:
        llm = LLMService()
        if not llm.configured:
            print("  ⚠ Gemini API not configured")
            return False
        
        result = await llm._generate_content("Say 'API working!' in one word")
        print(f"  ✅ Gemini API: {result[:50]}")
        return True
    except Exception as e:
        print(f"  ❌ Gemini API failed: {e}")
        return False

async def test_sheets():
    """Test Google Sheets"""
    print("\\n🔍 Testing Google Sheets API...")
    try:
        sheets = SheetsService()
        if not sheets.configured:
            print("  ⚠ Google Sheets not configured")
            return False
        
        items = await sheets.get_pending_content()
        print(f"  ✅ Google Sheets: Found {len(items)} pending items")
        return True
    except Exception as e:
        print(f"  ❌ Google Sheets failed: {e}")
        return False

async def test_slack():
    """Test Slack webhook"""
    print("\\n🔍 Testing Slack webhook...")
    try:
        slack = SlackService()
        if not slack.configured:
            print("  ⚠ Slack not configured")
            return False
        
        await slack.send_notification("API test message", "info")
        print("  ✅ Slack webhook working")
        return True
    except Exception as e:
        print(f"  ❌ Slack failed: {e}")
        return False

async def test_wordpress():
    """Test WordPress API"""
    print("\\n🔍 Testing WordPress API...")
    try:
        wp = WordPressService()
        if not wp.configured:
            print("  ⚠ WordPress not configured")
            return False
        
        print("  ✅ WordPress API configured")
        return True
    except Exception as e:
        print(f"  ❌ WordPress failed: {e}")
        return False

async def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("AI SOCIAL FACTORY - API TEST SUITE")
    print("=" * 60)
    
    results = {
        "Gemini": await test_gemini(),
        "Google Sheets": await test_sheets(),
        "Slack": await test_slack(),
        "WordPress": await test_wordpress()
    }
    
    print("\\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
    
    success_count = sum(results.values())
    total = len(results)
    print(f"\\nPassed: {success_count}/{total}")
    
    if success_count == total:
        print("\\n🎉 All tests passed!")
        return 0
    else:
        print("\\n⚠ Some tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
