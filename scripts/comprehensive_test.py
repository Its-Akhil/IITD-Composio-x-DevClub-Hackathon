#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Suite for AI Social Factory
Tests all components and endpoints from start to finish
"""
import sys
from pathlib import Path
import asyncio
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.services.llm_service import LLMService
from app.services.sheets_service import SheetsService
from app.services.slack_service import SlackService
from app.services.wordpress_service import WordPressService
import aiohttp

class ComprehensiveTest:
    """Comprehensive testing suite"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_key = settings.API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self.results = {}
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
    
    def print_header(self, text, char="="):
        """Print formatted header"""
        width = 80
        print(f"\n{char * width}")
        print(f"{text.center(width)}")
        print(f"{char * width}\n")
    
    def print_test(self, name, passed, message="", details=""):
        """Print test result"""
        self.test_count += 1
        if passed:
            self.passed_count += 1
            icon = "✅"
            status = "PASS"
        else:
            self.failed_count += 1
            icon = "❌"
            status = "FAIL"
        
        print(f"{icon} Test {self.test_count}: {name}")
        print(f"   Status: {status}")
        if message:
            print(f"   Message: {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.results[name] = {
            "passed": passed,
            "message": message,
            "details": details
        }
    
    async def test_server_health(self):
        """Test 1: Server Health Check"""
        self.print_header("PHASE 1: SERVER HEALTH CHECKS", "-")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as resp:
                    data = await resp.json()
                    self.print_test(
                        "Server Health Check",
                        resp.status == 200,
                        f"Server is {data.get('status', 'unknown')}",
                        f"Video Service: {data.get('video_service')}, Model Loaded: {data.get('model_loaded')}"
                    )
                    return data
        except Exception as e:
            self.print_test("Server Health Check", False, str(e))
            return None
    
    async def test_root_endpoint(self):
        """Test 2: Root Endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/") as resp:
                    data = await resp.json()
                    self.print_test(
                        "Root Endpoint",
                        resp.status == 200 and data.get('status') == 'operational',
                        f"API Version: {data.get('version')}",
                        f"Message: {data.get('message')}"
                    )
        except Exception as e:
            self.print_test("Root Endpoint", False, str(e))
    
    async def test_system_status(self):
        """Test 3: System Status"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/status") as resp:
                    data = await resp.json()
                    services = data.get('services', {})
                    resources = data.get('resources', {})
                    
                    all_services_up = all(services.values())
                    self.print_test(
                        "System Status Check",
                        resp.status == 200,
                        f"All services: {all_services_up}",
                        f"Services: {services}\nResources: {resources}"
                    )
                    return data
        except Exception as e:
            self.print_test("System Status Check", False, str(e))
            return None
    
    async def test_api_authentication(self):
        """Test 4: API Authentication"""
        self.print_header("PHASE 2: AUTHENTICATION & SECURITY", "-")
        
        # Test without API key
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/content/pending") as resp:
                    self.print_test(
                        "Authentication - No API Key",
                        resp.status in [401, 403],  # Either 401 or 403 is acceptable
                        f"Correctly rejected request without API key (status: {resp.status})"
                    )
        except Exception as e:
            self.print_test("Authentication - No API Key", False, str(e))
        
        # Test with valid API key
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/content/pending",
                    headers=self.headers
                ) as resp:
                    self.print_test(
                        "Authentication - Valid API Key",
                        resp.status in [200, 500],  # 500 if sheets not configured
                        "API key accepted"
                    )
        except Exception as e:
            self.print_test("Authentication - Valid API Key", False, str(e))
    
    async def test_external_services(self):
        """Test 5-8: External Service Integrations"""
        self.print_header("PHASE 3: EXTERNAL SERVICE INTEGRATIONS", "-")
        
        # Test Gemini API
        try:
            llm = LLMService()
            if llm.configured:
                result = await llm._generate_content("Say 'Hello World' in 2 words")
                self.print_test(
                    "Gemini API Integration",
                    bool(result),
                    "Successfully generated content",
                    f"Response: {result[:100]}..."
                )
            else:
                self.print_test("Gemini API Integration", False, "Not configured")
        except Exception as e:
            self.print_test("Gemini API Integration", False, str(e))
        
        # Test Google Sheets
        try:
            sheets = SheetsService()
            if sheets.configured:
                items = await sheets.get_pending_content()
                self.print_test(
                    "Google Sheets Integration",
                    True,
                    f"Found {len(items)} pending items",
                    f"Sheet configured and accessible"
                )
            else:
                self.print_test(
                    "Google Sheets Integration",
                    False,
                    "Not configured or no permission"
                )
        except Exception as e:
            self.print_test("Google Sheets Integration", False, str(e))
        
        # Test Slack
        try:
            slack = SlackService()
            if slack.configured:
                await slack.send_notification("🧪 Test notification from comprehensive test suite", "info")
                self.print_test(
                    "Slack Integration",
                    True,
                    "Test notification sent successfully"
                )
            else:
                self.print_test("Slack Integration", False, "Not configured")
        except Exception as e:
            self.print_test("Slack Integration", False, str(e))
        
        # Test WordPress
        try:
            wp = WordPressService()
            self.print_test(
                "WordPress Integration",
                wp.configured,
                "WordPress service configured" if wp.configured else "Not configured"
            )
        except Exception as e:
            self.print_test("WordPress Integration", False, str(e))
    
    async def test_llm_endpoints(self):
        """Test 9-11: LLM Service Endpoints"""
        self.print_header("PHASE 4: LLM SERVICE ENDPOINTS", "-")
        
        # Test script generation
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "topic": "AI and the Future of Work",
                    "duration": 60,
                    "tone": "educational",
                    "platform": "youtube"
                }
                async with session.post(
                    f"{self.base_url}/api/v1/content/generate-script",
                    headers=self.headers,
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.print_test(
                            "Script Generation Endpoint",
                            True,
                            f"Generated {len(data.get('variants', []))} script variants",
                            f"Topic: {data.get('topic')}"
                        )
                    else:
                        text = await resp.text()
                        self.print_test("Script Generation Endpoint", False, f"Status: {resp.status}", text[:200])
        except Exception as e:
            self.print_test("Script Generation Endpoint", False, str(e))
        
        # Test caption generation
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "script": "This is a test script about AI technology",
                    "platform": "instagram",
                    "include_hashtags": True
                }
                async with session.post(
                    f"{self.base_url}/api/v1/content/generate-caption",
                    headers=self.headers,
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.print_test(
                            "Caption Generation Endpoint",
                            True,
                            f"Generated caption with {len(data.get('hashtags', []))} hashtags",
                            f"Platform: {data.get('platform')}"
                        )
                    else:
                        text = await resp.text()
                        self.print_test("Caption Generation Endpoint", False, f"Status: {resp.status}", text[:200])
        except Exception as e:
            self.print_test("Caption Generation Endpoint", False, str(e))
    
    async def test_video_service(self):
        """Test 12: Video Service Status"""
        self.print_header("PHASE 5: VIDEO GENERATION SERVICE", "-")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/video/status",
                    headers=self.headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.print_test(
                            "Video Service Status",
                            True,
                            f"Model Loaded: {data.get('model_loaded')}, GPU: {data.get('gpu_available')}",
                            f"Device: {data.get('device')}"
                        )
                    else:
                        text = await resp.text()
                        self.print_test("Video Service Status", False, f"Status: {resp.status}", text)
        except Exception as e:
            self.print_test("Video Service Status", False, str(e))
    
    async def test_database(self):
        """Test 13: Database Connectivity"""
        self.print_header("PHASE 6: DATABASE & ANALYTICS", "-")
        
        try:
            from app.database import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
                self.print_test(
                    "Database Connectivity",
                    len(tables) > 0,
                    f"Found {len(tables)} tables",
                    f"Tables: {', '.join(tables)}"
                )
        except Exception as e:
            self.print_test("Database Connectivity", False, str(e))
    
    async def test_analytics_endpoint(self):
        """Test 14: Analytics Endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/analytics/summary?days=7",
                    headers=self.headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.print_test(
                            "Analytics Summary Endpoint",
                            True,
                            f"Period: {data.get('period', 'unknown')}",
                            f"Total Videos: {data.get('total_videos', 0)}"
                        )
                    else:
                        text = await resp.text()
                        self.print_test("Analytics Summary Endpoint", False, f"Status: {resp.status}", text[:200])
        except Exception as e:
            self.print_test("Analytics Summary Endpoint", False, str(e))
    
    async def test_file_system(self):
        """Test 15: File System & Directories"""
        self.print_header("PHASE 7: FILE SYSTEM & CONFIGURATION", "-")
        
        required_dirs = [
            "generated_videos",
            "logs",
            "local_t2v_model"
        ]
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            exists = dir_path.exists() and dir_path.is_dir()
            self.print_test(
                f"Directory: {dir_name}",
                exists,
                "Exists" if exists else "Missing"
            )
    
    async def test_configuration(self):
        """Test 16: Configuration Validation"""
        critical_configs = {
            "GEMINI_API_KEY": settings.GEMINI_API_KEY,
            "API_KEY": settings.API_KEY,
            "DATABASE_URL": settings.DATABASE_URL,
            "VIDEO_OUTPUT_DIR": settings.VIDEO_OUTPUT_DIR
        }
        
        for config_name, config_value in critical_configs.items():
            is_configured = bool(config_value and config_value != "")
            self.print_test(
                f"Config: {config_name}",
                is_configured,
                "Configured" if is_configured else "Not set"
            )
    
    def print_summary(self):
        """Print final test summary"""
        self.print_header("TEST SUMMARY", "=")
        
        print(f"Total Tests Run: {self.test_count}")
        print(f"✅ Passed: {self.passed_count}")
        print(f"❌ Failed: {self.failed_count}")
        
        success_rate = (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%\n")
        
        if self.failed_count == 0:
            print("🎉 ALL TESTS PASSED! Your AI Social Factory is fully operational!")
        elif success_rate >= 80:
            print("⚠️  Most tests passed. Review failures and fix critical issues.")
        elif success_rate >= 60:
            print("⚠️  Some tests failed. System is partially functional.")
        else:
            print("❌ Multiple failures detected. System needs attention.")
        
        print("\n" + "=" * 80)
        
        # Save results to file
        results_file = Path("logs") / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_tests": self.test_count,
                "passed": self.passed_count,
                "failed": self.failed_count,
                "success_rate": success_rate,
                "results": self.results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "=" * 80)
        print("AI SOCIAL FACTORY - COMPREHENSIVE TEST SUITE".center(80))
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(80))
        print("=" * 80)
        
        # Phase 1: Server Health
        health_data = await self.test_server_health()
        await self.test_root_endpoint()
        await self.test_system_status()
        
        # Phase 2: Authentication
        await self.test_api_authentication()
        
        # Phase 3: External Services
        await self.test_external_services()
        
        # Phase 4: LLM Endpoints
        await self.test_llm_endpoints()
        
        # Phase 5: Video Service
        await self.test_video_service()
        
        # Phase 6: Database & Analytics
        await self.test_database()
        await self.test_analytics_endpoint()
        
        # Phase 7: File System & Configuration
        await self.test_file_system()
        await self.test_configuration()
        
        # Print summary
        self.print_summary()

async def main():
    """Main test execution"""
    tester = ComprehensiveTest()
    await tester.run_all_tests()
    
    return 0 if tester.failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
