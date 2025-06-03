# ai-codereview
An AI-powered code review platform that automatically analyzes pull requests, detects security vulnerabilities, suggests improvements, and generates comprehensive documentation. It combines multiple AI tasks to provide a complete developer productivity solution.

NB. This code is not yet fully functional.

## What ai-codereview does

ai-codereview acts like a tireless code reviewer that:
- **Analyzes every pull request** automatically when you create or update it
- **Finds security vulnerabilities** before they reach production
- **Suggests improvements** to make your code better
- **Generates documentation** to help others understand your code
- **Provides quality scores** to track code health over time

## Key Features

### 🔍 **Multi-AI Analysis**
- Uses 5+ specialized AI models for comprehensive code review
- Text classification for issue categorization
- Security vulnerability detection
- Automatic documentation generation
- Code quality assessment

### 🔒 **Security First**
- Detects SQL injection vulnerabilities
- Identifies XSS risks
- Finds authentication bypasses
- Spots data exposure risks

### 📊 **Quality Metrics**
- Overall code quality scores (0-100)
- Complexity analysis
- Improvement suggestions
- Performance recommendations

### 🚀 **GitHub Integration**
- Automatic pull request analysis
- Real-time webhook processing
- Inline code comments
- Summary reports

## Quick Start

### 1. Clone the Repository
```
git clone https://github.com/crissyg/ai-codereview.git
cd ai-codereview
```

### 2. Set Up Environment
```
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### For GPU Support (if you have NVIDIA GPU):
# Replace torch line in the requirements.txt with:
```
torch==2.1.0+cu118
torchvision==0.16.0+cu118
torchaudio==2.1.0+cu118
```

### 3. Configure GitHub Token
```
# Create .env file
echo "GITHUB_TOKEN=ghp_your_github_token_here" > .env
```

### 4. Run the Application
```
# Start the API server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the System
```
# Test with sample code
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code_content": "def hello_world():\n    print(\"Hello, World!\")",
    "file_path": "example.py"
  }'
```

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub API    │────│   ai-codereview  │────│   AI Models     │
│   (Webhooks)    │    │ (Python/FastAPI) |    │   (HuggingFace) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │    Database      │
                       │   (PostgreSQL)   │
                       └──────────────────┘
```

## Project Structure

```
ai-codereview/
├── backend/
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── services/
│   │   │   ├── code_analyzer.py # AI analysis engine
│   │   │   └── github_integration.py # GitHub API client
│   │   ├── api/
│   │   │   └── routes.py        # API endpoints
│   │   └── utils/
│   │       └── config.py        # Configuration management
├── frontend/                    # Web dashboard (future)
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## API Endpoints

### Analyze Code
```
POST /api/v1/analyze
Content-Type: application/json

{
  "code_content": "your code here",
  "file_path": "path/to/file.py",
  "language": "python"
}
```

### GitHub Webhook
```
POST /api/v1/webhook/github
Content-Type: application/json

{
  "action": "opened",
  "pull_request": { ... },
  "repository": { ... }
}
```

### Health Check
```
GET /api/v1/health
```

## Configuration

Create a `.env` file with the following variables:

```
# Required
GITHUB_TOKEN=ghp_your_github_personal_access_token

# Optional
DATABASE_URL=postgresql://user:pass@localhost/ai_codereview
MODEL_CACHE_DIR=./cache
MAX_CONCURRENT_ANALYSES=5
DEBUG=false
```

## Deployment

### Using Docker Compose
```
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ai-codereview-api

# Stop services
docker-compose down
```

### Manual Deployment
```
# Install dependencies
pip install -r requirements.txt

# Start the application
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Performance Metrics Example

- **Analysis Speed**: ~2-5 seconds per file
- **Throughput**: 10,000+ daily analyses
- **Accuracy**: 85% security vulnerability detection
- **Uptime**: 99.9% availability target

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
