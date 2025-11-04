# Backend API Service

FastAPI-based backend service for HR CV Filter Agent.

## Features

- REST API endpoints for CV evaluation and chat
- MongoDB integration for custom rules management
- Google Gemini LLM integration
- CORS enabled for frontend communication

## API Endpoints

### Health Check
- `GET /health` - Check service health

### CV Evaluation
- `POST /api/evaluate-cv` - Evaluate CV against job description
  - Request body: `{cv_content, job_description, custom_rules, llm_model}`
  - Response: `{success, evaluation}`

### Chat
- `POST /api/chat` - Chat with agent
  - Request body: `{message, job_description, custom_rules, cv_evaluations, chat_history, llm_model}`
  - Response: `{success, response}`

### Rules Management
- `GET /api/rules` - Get all rules
- `GET /api/rules/names` - Get all rule names
- `GET /api/rules/{name}` - Get rule by name
- `POST /api/rules` - Create new rule
- `PUT /api/rules/{name}` - Update rule
- `DELETE /api/rules/{name}` - Delete rule

## Running Locally

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run server
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at:
- http://localhost:8000
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Required:
- `GOOGLE_API_KEY` - Google Gemini API key
- `MONGO_URI` - MongoDB connection URI
- `MONGO_DB` - MongoDB database name (default: hr_cv_filter_agent)
- `MONGO_COLLECTION` - MongoDB collection name (default: rules)

