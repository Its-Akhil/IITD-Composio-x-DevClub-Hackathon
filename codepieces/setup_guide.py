
# Create a comprehensive project setup guide
setup_guide = """
╔══════════════════════════════════════════════════════════════════════╗
║         AI SOCIAL FACTORY - PYTHON BACKEND SETUP GUIDE               ║
╚══════════════════════════════════════════════════════════════════════╝

COMPLETE PROJECT STRUCTURE GENERATED!

📁 Project Files: 36 files
   - 22 Python modules
   - 6 Configuration files  
   - 8 Package markers

═══════════════════════════════════════════════════════════════════════

🚀 QUICK START GUIDE

STEP 1: Create Project Directory
─────────────────────────────────
mkdir ai-social-factory
cd ai-social-factory

STEP 2: Create All Directories
─────────────────────────────────
mkdir -p app/api/routes app/services app/core app/utils
mkdir -p tests scripts generated_videos logs local_t2v_model

STEP 3: Copy Generated Files
─────────────────────────────────
Copy all 36 generated files to their respective directories following
the project structure shown above.

File Organization:
  app/              → Core application code
  app/api/routes/   → API endpoint definitions
  app/services/     → Business logic services
  app/core/         → Core utilities (security, logging, exceptions)
  app/utils/        → Helper utilities
  scripts/          → Setup and utility scripts
  tests/            → Test suite

STEP 4: Create Virtual Environment
─────────────────────────────────
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\\Scripts\\activate    # Windows

STEP 5: Install Dependencies
─────────────────────────────────
pip install --upgrade pip
pip install -r requirements.txt

This will install:
  - FastAPI & Uvicorn (Web framework)
  - PyTorch & Diffusers (Video generation)
  - Google Generative AI (Gemini)
  - gspread (Google Sheets)
  - aiohttp (Async HTTP client)
  - SQLAlchemy (Database ORM)
  - And 15+ other dependencies

STEP 6: Configure Environment
─────────────────────────────────
cp .env.example .env
nano .env  # Or your preferred editor

Required configuration:
  ✓ GEMINI_API_KEY              (Get from ai.google.dev)
  ✓ GOOGLE_SHEETS_SPREADSHEET_ID (Your spreadsheet ID)
  ✓ SLACK_WEBHOOK_URL            (Create webhook in Slack)
  ✓ WORDPRESS_SITE_URL           (Your WordPress site)
  ✓ WORDPRESS_USERNAME           (WP username)
  ✓ WORDPRESS_APP_PASSWORD       (Generate in WP profile)
  ✓ API_KEY                      (Set your own secure key)

Optional configuration:
  - GOOGLE_SHEETS_CREDENTIALS_FILE (Path to credentials.json)
  - VIDEO_NUM_FRAMES              (Default: 16)
  - VIDEO_HEIGHT/WIDTH            (Default: 256x256)
  - USE_GPU                       (true if GPU available)

STEP 7: Setup Google Sheets
─────────────────────────────────
1. Create a new Google Sheet with these columns:
   Date | Topic | Video_Prompt | Status | Video_URL | Platform | Approved_By | Post_ID | Timestamp

2. Create Google Cloud Project:
   - Go to console.cloud.google.com
   - Enable Google Sheets API
   - Create Service Account
   - Download credentials.json
   - Save to project root

3. Share spreadsheet with service account email

STEP 8: Download AI Model
─────────────────────────────────
python scripts/download_model.py

⏳ This will:
  - Download ModelScope text-to-video-ms-1.7b (~6GB)
  - Cache model in ./local_t2v_model/
  - Take 10-15 minutes depending on connection
  - Require ~10GB free disk space

Note: Skip this if you don't have GPU - model will download on first use

STEP 9: Initialize Database
─────────────────────────────────
python scripts/setup_db.py

Creates SQLite database with tables:
  - video_generations
  - workflow_executions

STEP 10: Test API Connections
─────────────────────────────────
python scripts/test_apis.py

This will verify:
  ✓ Gemini API (LLM service)
  ✓ Google Sheets API (Content calendar)
  ✓ Slack Webhook (Approvals)
  ✓ WordPress API (Publishing)

STEP 11: Run the Application
─────────────────────────────────
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Server will start at: http://localhost:8000

═══════════════════════════════════════════════════════════════════════

📚 ACCESSING THE API

API Documentation (Swagger UI):
  → http://localhost:8000/docs

Alternative API Docs (ReDoc):
  → http://localhost:8000/redoc

Health Check:
  → http://localhost:8000/health

System Status:
  → http://localhost:8000/api/v1/status

Generated Videos:
  → http://localhost:8000/videos/{video_id}.mp4

═══════════════════════════════════════════════════════════════════════

🔧 TESTING THE WORKFLOW

1. Add Test Content to Google Sheets
─────────────────────────────────
Open your spreadsheet and add a row:
  Date: 2025-10-22
  Topic: Future of AI
  Video_Prompt: A futuristic city with flying cars
  Status: Pending
  Platform: instagram

2. Process the Content
─────────────────────────────────
curl -X POST http://localhost:8000/api/v1/workflow/execute \\
  -H "X-API-Key: your-api-key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "content_id": 2,
    "skip_approval": false,
    "auto_publish": false
  }'

3. Check Slack for Approval
─────────────────────────────────
The workflow will:
  ✓ Analyze the topic (Gemini)
  ✓ Generate 3 script variants (Gemini)
  ✓ Create video (ModelScope)
  ✓ Generate caption (Gemini)
  ✓ Send approval request to Slack
  ⏸ Wait for approval

4. Approve in Slack
─────────────────────────────────
Click ✅ Approve button in #content-review channel

5. Verify Publication
─────────────────────────────────
Check your WordPress site for the new post!

═══════════════════════════════════════════════════════════════════════

🐳 DOCKER DEPLOYMENT (ALTERNATIVE)

If you prefer Docker:

1. Build and Start
─────────────────────────────────
docker-compose up -d

2. View Logs
─────────────────────────────────
docker-compose logs -f api

3. Stop Services
─────────────────────────────────
docker-compose down

Note: GPU support in Docker requires nvidia-docker runtime

═══════════════════════════════════════════════════════════════════════

📊 MONITORING & LOGS

Application Logs:
  → ./logs/app.log

Real-time Monitoring:
  tail -f logs/app.log | grep ERROR

Check Generated Videos:
  ls -lh generated_videos/

Database:
  sqlite3 ai_social_factory.db
  .tables
  SELECT * FROM video_generations LIMIT 5;

═══════════════════════════════════════════════════════════════════════

⚡ PERFORMANCE OPTIMIZATION

1. Enable GPU (if available)
─────────────────────────────────
In .env:
  USE_GPU=true

Verify GPU:
  nvidia-smi
  python -c "import torch; print(torch.cuda.is_available())"

2. Adjust Video Settings
─────────────────────────────────
For faster generation (lower quality):
  VIDEO_NUM_FRAMES=8
  VIDEO_HEIGHT=128
  VIDEO_WIDTH=128

For better quality (slower):
  VIDEO_NUM_FRAMES=24
  VIDEO_HEIGHT=512
  VIDEO_WIDTH=512

3. Concurrent Processing
─────────────────────────────────
In .env:
  MAX_CONCURRENT_VIDEOS=3

═══════════════════════════════════════════════════════════════════════

🐛 TROUBLESHOOTING

Problem: ImportError for 'google.generativeai'
Solution: pip install google-generativeai==0.3.2

Problem: CUDA out of memory
Solution: Reduce VIDEO_NUM_FRAMES or VIDEO_HEIGHT/WIDTH

Problem: Gemini API 429 (Rate Limit)
Solution: You've hit 250 requests/day limit. Wait or upgrade tier.

Problem: Slack webhook not working
Solution: Verify webhook URL format and test with curl

Problem: WordPress 401 Unauthorized
Solution: Regenerate Application Password in WordPress profile

Problem: Google Sheets permission denied
Solution: Share spreadsheet with service account email

Problem: Model download stuck
Solution: Check internet connection and free disk space (need 10GB)

═══════════════════════════════════════════════════════════════════════

🎯 NEXT STEPS

1. ✅ Run scripts/test_apis.py to verify all services
2. ✅ Generate your first video via API
3. ✅ Test full workflow with one content item
4. ✅ Set up cron job for automated daily processing
5. ✅ Monitor logs and success rates
6. ✅ Optimize prompts for better content quality
7. ✅ Scale to 5-10 videos/day
8. ✅ Consider upgrading video model for production

═══════════════════════════════════════════════════════════════════════

📝 CRON JOB SETUP (Optional)

To run daily processing automatically:

1. Create cron_process.sh:
─────────────────────────────────
#!/bin/bash
cd /path/to/ai-social-factory
source venv/bin/activate
curl -X POST http://localhost:8000/api/v1/workflow/process-all \\
  -H "X-API-Key: your-api-key"

2. Make executable:
─────────────────────────────────
chmod +x cron_process.sh

3. Add to crontab:
─────────────────────────────────
crontab -e

Add line:
0 6 * * * /path/to/ai-social-factory/cron_process.sh >> /path/to/logs/cron.log 2>&1

This runs daily at 6 AM.

═══════════════════════════════════════════════════════════════════════

💡 TIPS FOR SUCCESS

1. Start Small: Test with 1-2 videos before scaling
2. Monitor Costs: Gemini free tier = 250 requests/day
3. Quality Check: Review first 10 videos carefully
4. Backup Data: Keep backups of generated_videos/ and database
5. Version Control: Commit to git regularly
6. Security: Never commit .env or credentials.json
7. Documentation: Keep notes on what prompts work best
8. Community: Share learnings and improvements

═══════════════════════════════════════════════════════════════════════

📧 SUPPORT & RESOURCES

Documentation: See README.md for detailed API reference
Issues: Check logs/app.log for error details
Community: [Add your discussion forum URL]
Updates: [Add your GitHub/GitLab URL]

═══════════════════════════════════════════════════════════════════════

Good luck with your AI Social Factory! 🚀

═══════════════════════════════════════════════════════════════════════
"""

print(setup_guide)

# Create a summary CSV for easy reference
import pandas as pd

files_data = {
    'File Path': [
        'app/main.py',
        'app/config.py',
        'app/models.py',
        'app/database.py',
        'app/services/video_service.py',
        'app/services/llm_service.py',
        'app/services/sheets_service.py',
        'app/services/slack_service.py',
        'app/services/wordpress_service.py',
        'app/services/workflow_service.py',
        'app/api/routes/video.py',
        'app/api/routes/workflow.py',
        'app/api/routes/content.py',
        'app/api/routes/analytics.py',
        'app/core/security.py',
        'app/core/logging.py',
        'app/core/exceptions.py',
        'app/utils/file_utils.py',
        'app/utils/validators.py',
        'scripts/download_model.py',
        'scripts/setup_db.py',
        'scripts/test_apis.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'Dockerfile',
        'docker-compose.yml',
        'README.md'
    ],
    'Description': [
        'FastAPI application entry point',
        'Configuration management with Pydantic',
        'Pydantic request/response models',
        'SQLAlchemy database ORM',
        'ModelScope video generation service',
        'Google Gemini API integration',
        'Google Sheets API integration',
        'Slack webhook integration',
        'WordPress REST API integration',
        'Workflow orchestration service',
        'Video generation API endpoints',
        'Workflow management API endpoints',
        'Content calendar API endpoints',
        'Analytics API endpoints',
        'API key authentication',
        'Logging configuration',
        'Custom exception classes',
        'File operation utilities',
        'Input validation utilities',
        'Script to download ModelScope model',
        'Script to initialize database',
        'Script to test API connections',
        'Python dependencies',
        'Environment variables template',
        'Git ignore patterns',
        'Docker container definition',
        'Docker Compose configuration',
        'Project documentation'
    ],
    'Purpose': [
        'Application lifecycle, routing, middleware',
        'Centralized settings management',
        'Type-safe data validation',
        'Database schema and session management',
        'Generate videos from text prompts',
        'AI script and caption generation',
        'Content calendar data access',
        'Approval workflow notifications',
        'Auto-publish content to WordPress',
        'Coordinate full content pipeline',
        'REST API for video generation',
        'REST API for workflow execution',
        'REST API for content management',
        'REST API for analytics',
        'Secure API endpoints',
        'Structured application logging',
        'Error handling',
        'File management helpers',
        'Input sanitization and validation',
        'One-time model download',
        'Database initialization',
        'Configuration verification',
        'Package dependencies',
        'Configuration template',
        'Version control exclusions',
        'Containerization',
        'Multi-container orchestration',
        'Setup and usage guide'
    ]
}

df = pd.DataFrame(files_data)
csv_output = df.to_csv(index=False)

print("\n\n" + "=" * 70)
print("FILE REFERENCE SUMMARY (CSV)")
print("=" * 70)
print(csv_output)

# Save to CSV file
with open('/tmp/ai_social_factory_files.csv', 'w') as f:
    f.write(csv_output)

print("\n✅ CSV file saved to: /tmp/ai_social_factory_files.csv")
print("\nPython backend project generation complete!")
print("\nYou now have a complete, production-ready backend with:")
print("  ✓ 22 Python modules")
print("  ✓ 6 configuration files")
print("  ✓ 8 package markers")
print("  ✓ Full API documentation")
print("  ✓ Docker deployment support")
print("  ✓ Comprehensive setup guide")