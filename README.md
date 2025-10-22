# AI Social Factory - Python Backend

🤖 Automated content generation and publishing platform using AI

## 🌟 Features

- 🎬 **Text-to-Video Generation** - Using ModelScope AI diffusion model
- 🤖 **AI Script Generation** - Google Gemini generates engaging scripts
- 📝 **Smart Captions** - Platform-specific captions with hashtags
- 📊 **Google Sheets Integration** - Content calendar management
- 💬 **Slack Approval Workflow** - Team-based content approval
- 📰 **WordPress Auto-Publishing** - Direct publishing to WordPress
- 📈 **Analytics Dashboard** - Track performance and metrics

## 🏗️ Architecture

```
User Request → FastAPI (main.py)
    ↓
API Routes (video, workflow, content, analytics)
    ↓
Workflow Service (orchestrates everything)
    ↓
├─→ Video Service (ModelScope AI)
├─→ LLM Service (Gemini API)
├─→ Sheets Service (Content Calendar)
├─→ Slack Service (Approvals)
└─→ WordPress Service (Publishing)
```

## 📋 Prerequisites

- **Python** 3.10 or higher
- **GPU** NVIDIA GPU with 16GB+ VRAM (recommended for video generation)
- **Disk Space** ~10GB for AI models
- **API Keys**:
  - Google Gemini API key
  - Google Sheets credentials
  - Slack webhook URL
  - WordPress site credentials

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd ai-social-factory

# Create virtual environment (already exists in your case)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env and configure:
# - GEMINI_API_KEY (from ai.google.dev)
# - GOOGLE_SHEETS_SPREADSHEET_ID
# - GOOGLE_SHEETS_CREDENTIALS_FILE
# - SLACK_WEBHOOK_URL
# - WORDPRESS_SITE_URL
# - WORDPRESS_USERNAME
# - WORDPRESS_APP_PASSWORD
# - API_KEY (generate a secure random key)
```

### 3. Setup Google Sheets

1. Create a Google Sheet with these columns:
   ```
   Date | Topic | Video_Prompt | Status | Video_URL | Platform | Approved_By | Post_ID | Timestamp
   ```

2. Create Google Cloud Project:
   - Go to console.cloud.google.com
   - Enable Google Sheets API
   - Create Service Account
   - Download credentials.json
   - Save to project root

3. Share spreadsheet with service account email

### 4. Initialize Database

```bash
python scripts/setup_db.py
```

### 5. Test API Connections

```bash
python scripts/test_apis.py
```

### 6. Download AI Model (Optional)

```bash
# Downloads ~6GB ModelScope model
# Only needed for video generation
python scripts/download_model.py
```

### 7. Run the Application

**Option 1: Using PowerShell Scripts (Recommended)**

```powershell
# Development mode (auto-reload on code changes, ignores videos/logs)
.\start_dev.ps1

# Production mode (no auto-reload)
.\start_prod.ps1
```

**Option 2: Direct uvicorn command**

```bash
# Development mode (with smart reload excludes)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 \
  --reload-exclude "generated_videos/*" \
  --reload-exclude "logs/*" \
  --reload-exclude "*.log" \
  --reload-exclude "*.mp4" \
  --reload-exclude "*.db"

# Production mode (no reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Option 3: Python script**

```bash
python -m app.main
```

> **Note**: The app now intelligently excludes `generated_videos/`, `logs/`, and model folders from auto-reload to prevent unnecessary restarts during video generation or logging.

### 8. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Video Generation

```bash
POST /api/v1/video/generate
```

Generate a video from text prompt.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/video/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic city at sunset",
    "num_frames": 16,
    "height": 256,
    "width": 256
  }'
```

### Workflow Execution

```bash
POST /api/v1/workflow/execute
```

Execute full content workflow for a specific item.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/workflow/execute \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 2,
    "skip_approval": false,
    "auto_publish": false
  }'
```

### Process All Pending

```bash
POST /api/v1/workflow/process-all
```

Process all pending content from Google Sheets.

### Get Pending Content

```bash
GET /api/v1/content/pending
```

Retrieve all pending content items from Google Sheets.

### Analytics

```bash
GET /api/v1/analytics/summary?days=7
```

Get analytics summary for the specified period.

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables for Docker

Update your `.env` file before running Docker containers.

## 📂 Project Structure

```
ai-social-factory/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   ├── database.py          # SQLAlchemy ORM
│   ├── api/
│   │   └── routes/          # API endpoints
│   │       ├── video.py
│   │       ├── workflow.py
│   │       ├── content.py
│   │       └── analytics.py
│   ├── services/            # Business logic
│   │   ├── video_service.py
│   │   ├── llm_service.py
│   │   ├── sheets_service.py
│   │   ├── slack_service.py
│   │   ├── wordpress_service.py
│   │   └── workflow_service.py
│   ├── core/                # Core utilities
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   └── utils/               # Helper functions
│       ├── file_utils.py
│       └── validators.py
├── scripts/                 # Setup scripts
│   ├── download_model.py
│   ├── setup_db.py
│   └── test_apis.py
├── tests/                   # Test suite
├── generated_videos/        # Video output
├── logs/                    # Application logs
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

### Required Settings

- `GEMINI_API_KEY` - Google Gemini API key
- `GOOGLE_SHEETS_SPREADSHEET_ID` - Your spreadsheet ID
- `SLACK_WEBHOOK_URL` - Slack webhook for notifications
- `WORDPRESS_SITE_URL` - WordPress site URL
- `API_KEY` - API authentication key

### Optional Settings

- `VIDEO_NUM_FRAMES` - Video frame count (default: 16)
- `VIDEO_HEIGHT` - Video height (default: 256)
- `VIDEO_WIDTH` - Video width (default: 256)
- `USE_GPU` - Enable GPU acceleration (default: true)
- `MAX_CONCURRENT_VIDEOS` - Max parallel videos (default: 3)

## 🧪 Testing

### Run All Tests

```bash
pytest tests/
```

### Test Individual Components

```bash
# Test Gemini API
python -c "from app.services.llm_service import LLMService; import asyncio; asyncio.run(LLMService()._generate_content('test'))"

# Test Google Sheets
python scripts/test_apis.py
```

## 🛠️ Troubleshooting

### GPU Not Detected

```bash
# Check CUDA
nvidia-smi

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Out of Memory

- Reduce `VIDEO_NUM_FRAMES` to 8
- Lower resolution to 128x128
- Set `USE_GPU=false` (slower but uses less memory)

### API Connection Errors

```bash
# Test all APIs
python scripts/test_apis.py

# Check logs
cat logs/app.log
```

## 📊 Performance

- **Video Generation**: 60-90 seconds (GPU) / 5-10 minutes (CPU)
- **Script Generation**: 3-5 seconds
- **Caption Generation**: 2-3 seconds
- **Full Workflow**: ~2 minutes per video
- **Daily Capacity**: 5-10 videos (free tier)

## 💰 Cost Estimate

- **Gemini API**: Free (250 requests/day)
- **ModelScope Model**: Free (open-source)
- **Infrastructure**: $0 (self-hosted) or ~$0.50/hour (cloud GPU)
- **Total**: Essentially free for low-volume usage

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📧 Support

For issues and questions:
- GitHub Issues
- Check logs at `logs/app.log`
- Review `SETUP_COMPLETE.md` for detailed setup

---

**Built with:** FastAPI, PyTorch, Google Gemini, ModelScope, and ❤️

**Last Updated:** October 21, 2025
