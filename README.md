# HR CV Filter Agent

An intelligent HR CV filtering system powered by Google Gemini AI. This application helps HR professionals automate CV screening and evaluation against job descriptions.

## Architecture

This application follows a **microservices architecture** with two main services:

- **Backend API Service** (FastAPI): Handles AI agent logic, LLM operations, and MongoDB interactions
- **Frontend UI Service** (Vite + React): Provides modern, responsive user interface and communicates with backend via REST API

```
┌─────────────────┐         HTTP/REST API        ┌─────────────────┐
│                 │ ◄──────────────────────────► │                 │
│  Frontend UI    │                              │  Backend API    │
│  (Vite+React)   │                              │  (FastAPI)      │
│  Port: 8501     │                              │  Port: 8000     │
│                 │                              │                 │
└─────────────────┘                              └────────┬────────┘
                                                          │
                                                          │
                                                          ▼
                                                  ┌───────────────┐
                                                  │   MongoDB     │
                                                  │   (Rules DB)  │
                                                  └───────────────┘
```

## Features

- 📄 **Multi-format CV Support**: Upload CVs in PDF, DOCX, TXT, or MD formats
- 🤖 **AI-Powered Evaluation**: Uses Google Gemini to analyze and evaluate CVs
- 📋 **Custom Rules Management**: Create, update, delete evaluation rules stored in MongoDB
- 💬 **Interactive Chat**: Ask questions about evaluated CVs
- 🎯 **Job Description Matching**: Automatically matches CVs against job requirements
- 🔄 **Dynamic Context**: Agent automatically reads all available fields and provides hints
- 💾 **MongoDB Integration**: Persistent storage for custom evaluation rules

## Prerequisites

- Python 3.10+ (for backend)
- Node.js 20+ (for frontend)
- Google API Key (Gemini)
- MongoDB Atlas account or local MongoDB instance
- Docker & Docker Compose (for containerized deployment)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd HR_CVFilter_Agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend && npm install

# Or install all at once
make install
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Add your credentials to `.env`:
```
GOOGLE_API_KEY=your_google_api_key_here
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=hr_cv_filter_agent
MONGO_COLLECTION=rules
```

6. Run the services:

**Option 1: Run both services together**
```bash
make run
```

**Option 2: Run services separately**

Terminal 1 (Backend):
```bash
make run-backend
# Backend API will be available at http://localhost:8000
```

Terminal 2 (Frontend):
```bash
make run-frontend
# Frontend UI will be available at http://localhost:8501
```

The frontend will be available at `http://localhost:8501`
The backend API docs will be available at `http://localhost:8000/docs`

### Docker Deployment

1. Make sure you have Docker and Docker Compose installed

2. Create `.env` file with your Google API key:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application at `http://localhost:8501`

5. View logs:
```bash
docker-compose logs -f
```

6. Stop the application:
```bash
docker-compose down
```

## Usage

1. **Enter Job Description**: Paste the job description in the left panel
2. **Manage Custom Rules**:
   - Select existing rules from dropdown
   - Create new rules with name and content
   - Update or delete existing rules
   - All rules are stored in MongoDB
3. **Upload CVs**: Upload one or multiple CV files
4. **Review Evaluations**: View AI-generated evaluations for each CV
5. **Chat with Agent**: Ask questions about the evaluated CVs

## Project Structure

```
HR_CVFilter_Agent/
├── backend/                    # Backend API Service
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Backend dependencies
│   ├── Dockerfile            # Backend Docker config
│   └── __init__.py
├── frontend/                   # Frontend UI Service
│   ├── src/                  # React source code
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   └── utils/            # Utility functions
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── nginx.conf            # Nginx configuration for production
│   └── Dockerfile            # Frontend Docker config
├── src/                       # Shared source code
│   ├── agent/
│   │   └── HR_CVFilter_agent.py   # Main agent logic
│   ├── llms/
│   │   └── geminiLLM.py          # Gemini LLM wrapper
│   ├── models/
│   │   └── rule_model.py         # MongoDB rule model
│   ├── services/
│   │   └── rule_service.py       # MongoDB CRUD service
│   ├── prompt/
│   │   ├── context_builder.py    # Context building logic
│   │   └── system_prompt.md      # System prompt template
│   └── utils/
│       ├── cv_extractor.py       # CV text extraction
│       └── logger.py             # Logging utility
├── docker-compose.yml          # Docker Compose for microservices
├── Makefile                    # Build and run commands
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Components

### Backend API Service (FastAPI)
- **REST API Endpoints**: `/api/evaluate-cv`, `/api/chat`, `/api/rules/*`
- **Agent Orchestration**: Manages CV evaluation and chat interactions
- **LLM Integration**: Communicates with Google Gemini API
- **MongoDB Service**: CRUD operations for custom rules
- **Port**: 8000

### Frontend UI Service (Vite + React)
- **Modern UI Framework**: Built with React and TypeScript for better performance
- **Responsive Design**: Clean, modern interface with better UX
- **API Client**: Communicates with backend via HTTP using Axios
- **CV Extraction**: Client-side text extraction from PDF, DOCX, TXT, MD files
- **Production Ready**: Nginx-based production deployment
- **Port**: 8501

### Shared Components
- **Context Builder**: Dynamically builds prompts with job description, custom rules, and hints
- **Rule Model**: Data model for evaluation rules
- **Logger**: Centralized logging utility

## Key Features

### Dynamic Context Building
The agent automatically:
- Reads all available fields (job description, custom rules, CV content)
- Provides hints if information is missing
- Recreates context for each interaction

### Smart Evaluation
- Evaluates CVs against job descriptions
- Applies custom rules
- Maintains conversation history
- Provides detailed analysis

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `MONGO_URI` | MongoDB connection URI | Yes |
| `MONGO_DB` | MongoDB database name | No (default: hr_cv_filter_agent) |
| `MONGO_COLLECTION` | MongoDB collection name | No (default: rules) |

## Docker Configuration

### Dockerfile
- Base image: `python:3.10-slim`
- Exposes port: `8501`
- Includes health check

### docker-compose.yml
- Service name: `hr-cv-filter-agent`
- Port mapping: `8501:8501`
- Auto-restart: `unless-stopped`
- Network: `hr-cv-network`

## Troubleshooting

### API Key Issues
If you see "Your default credentials were not found":
- Make sure `.env` file exists
- Verify `GOOGLE_API_KEY` is set correctly
- Restart the application

### Docker Issues
If container fails to start:
```bash
docker-compose logs hr-cv-filter-agent
```

### MongoDB Connection Issues
If you see "Failed to connect to MongoDB":
- Verify `MONGO_URI` is correct in `.env` file
- Check MongoDB Atlas network access settings
- Ensure your IP is whitelisted in MongoDB Atlas
- Test connection using MongoDB Compass

### Port Already in Use
If port 8501 is already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Use different external port
```

## License

Apache License 2.0