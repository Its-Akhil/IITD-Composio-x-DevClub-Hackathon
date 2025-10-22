#!/usr/bin/env python3
"""
Verify Google Sheets setup and provide detailed diagnostics
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from app.config import settings

def check_credentials_file():
    """Check if credentials file exists and is valid"""
    print("=" * 70)
    print("1. CHECKING CREDENTIALS FILE")
    print("=" * 70)
    
    try:
        with open(settings.GOOGLE_SHEETS_CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
        
        print(f"✅ File exists: {settings.GOOGLE_SHEETS_CREDENTIALS_FILE}")
        print(f"✅ Type: {creds.get('type')}")
        print(f"✅ Project ID: {creds.get('project_id')}")
        print(f"\n📧 Service Account Email:")
        print(f"   {creds.get('client_email')}")
        print(f"\n⚠️  IMPORTANT: This email must have Editor access to your spreadsheet!")
        return True, creds.get('client_email')
    except FileNotFoundError:
        print(f"❌ File not found: {settings.GOOGLE_SHEETS_CREDENTIALS_FILE}")
        return False, None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in credentials file")
        return False, None
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False, None

def check_spreadsheet_config():
    """Check spreadsheet configuration"""
    print("\n" + "=" * 70)
    print("2. CHECKING SPREADSHEET CONFIGURATION")
    print("=" * 70)
    
    print(f"📊 Spreadsheet ID: {settings.GOOGLE_SHEETS_SPREADSHEET_ID}")
    print(f"📄 Sheet Name: {settings.GOOGLE_SHEETS_SHEET_NAME}")
    
    if not settings.GOOGLE_SHEETS_SPREADSHEET_ID:
        print("❌ Spreadsheet ID not configured!")
        return False
    
    spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{settings.GOOGLE_SHEETS_SPREADSHEET_ID}/edit"
    print(f"\n🔗 Spreadsheet URL:")
    print(f"   {spreadsheet_url}")
    
    return True

def test_connection(service_email):
    """Test connection to Google Sheets"""
    print("\n" + "=" * 70)
    print("3. TESTING CONNECTION")
    print("=" * 70)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        print("⏳ Authenticating...")
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
            scopes=scopes
        )
        
        print("⏳ Connecting to Google Sheets...")
        client = gspread.authorize(creds)
        
        print("⏳ Opening spreadsheet...")
        spreadsheet = client.open_by_key(settings.GOOGLE_SHEETS_SPREADSHEET_ID)
        
        print(f"✅ Successfully connected!")
        print(f"✅ Spreadsheet title: {spreadsheet.title}")
        
        # Check for the specific worksheet
        print(f"\n⏳ Looking for worksheet: {settings.GOOGLE_SHEETS_SHEET_NAME}")
        try:
            worksheet = spreadsheet.worksheet(settings.GOOGLE_SHEETS_SHEET_NAME)
            print(f"✅ Worksheet found!")
            print(f"✅ Rows: {worksheet.row_count}")
            print(f"✅ Columns: {worksheet.col_count}")
            
            # Get headers
            headers = worksheet.row_values(1)
            if headers:
                print(f"\n📋 Current columns:")
                for i, header in enumerate(headers, 1):
                    print(f"   {i}. {header}")
                
                # Check required columns
                required = ['Date', 'Topic', 'Video_Prompt', 'Status']
                missing = [col for col in required if col not in headers]
                
                if missing:
                    print(f"\n⚠️  Missing recommended columns: {', '.join(missing)}")
                else:
                    print(f"\n✅ All required columns present!")
            
            return True
            
        except gspread.exceptions.WorksheetNotFound:
            print(f"❌ Worksheet '{settings.GOOGLE_SHEETS_SHEET_NAME}' not found!")
            print(f"\nAvailable worksheets:")
            for ws in spreadsheet.worksheets():
                print(f"   - {ws.title}")
            return False
            
    except PermissionError:
        print("❌ PERMISSION DENIED!")
        print(f"\n🔧 FIX: Share your spreadsheet with this service account:")
        print(f"   📧 {service_email}")
        print(f"   🔓 Permission level: Editor")
        print(f"\n📝 Steps:")
        print(f"   1. Open: https://docs.google.com/spreadsheets/d/{settings.GOOGLE_SHEETS_SPREADSHEET_ID}/edit")
        print(f"   2. Click 'Share' button")
        print(f"   3. Add: {service_email}")
        print(f"   4. Set as: Editor")
        print(f"   5. Click 'Send'")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def print_summary(creds_ok, config_ok, connection_ok):
    """Print final summary"""
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    status = {
        "Credentials File": creds_ok,
        "Configuration": config_ok,
        "Connection": connection_ok
    }
    
    for item, ok in status.items():
        icon = "✅" if ok else "❌"
        print(f"{icon} {item}")
    
    print("\n")
    
    if all(status.values()):
        print("🎉 GOOGLE SHEETS SETUP COMPLETE!")
        print("\nYou can now run: python scripts\\test_apis.py")
    else:
        print("⚠️  SETUP INCOMPLETE - Please fix the issues above")
        print("\nFor help, see: GOOGLE_SHEETS_SETUP.md")

def main():
    """Main function"""
    print("\n🔍 GOOGLE SHEETS SETUP VERIFICATION")
    print(f"Time: {__import__('datetime').datetime.now()}")
    print()
    
    # Run checks
    creds_ok, service_email = check_credentials_file()
    config_ok = check_spreadsheet_config()
    
    if creds_ok and config_ok:
        connection_ok = test_connection(service_email)
    else:
        connection_ok = False
    
    # Print summary
    print_summary(creds_ok, config_ok, connection_ok)
    
    return 0 if all([creds_ok, config_ok, connection_ok]) else 1

if __name__ == "__main__":
    sys.exit(main())
