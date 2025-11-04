# HR CV Filter Agent

An intelligent HR CV filtering system powered by Google Gemini AI. This application helps HR professionals automate CV screening and evaluation against job descriptions.

## Features

- 📄 **Multi-format CV Support**: Upload CVs in PDF, DOCX, TXT, or MD formats
- 🤖 **AI-Powered Evaluation**: Uses Google Gemini to analyze and evaluate CVs
- 📋 **Custom Rules**: Define custom evaluation criteria
- 💬 **Interactive Chat**: Ask questions about evaluated CVs
- 🎯 **Job Description Matching**: Automatically matches CVs against job requirements
- 🔄 **Dynamic Context**: Agent automatically reads all available fields and provides hints

## Prerequisites

- Python 3.10+
- Google API Key (Gemini)
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
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Add your Google API key to `.env`:
```
GOOGLE_API_KEY=your_google_api_key_here
```

6. Run the application:
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

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
2. **Set Custom Rules** (Optional): Add specific evaluation criteria
3. **Upload CVs**: Upload one or multiple CV files
4. **Review Evaluations**: View AI-generated evaluations for each CV
5. **Chat with Agent**: Ask questions about the evaluated CVs

## Project Structure

```
HR_CVFilter_Agent/
├── app.py                      # Main Streamlit application
├── src/
│   ├── agent/
│   │   └── HR_CVFilter_agent.py   # Main agent logic
│   ├── llms/
│   │   └── geminiLLM.py          # Gemini LLM wrapper
│   ├── prompt/
│   │   ├── context_builder.py    # Context building logic
│   │   └── system_prompt.md      # System prompt template
│   ├── utils/
│   │   ├── cv_extractor.py       # CV text extraction
│   │   └── logger.py             # Logging utility
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Architecture

The application follows a clean architecture pattern:

- **Context Builder**: Dynamically builds prompts with job description, custom rules, and hints
- **Agent**: Orchestrates CV evaluation and chat interactions
- **LLM Wrapper**: Handles communication with Google Gemini API
- **CV Extractor**: Extracts text from various document formats
- **Streamlit UI**: Provides interactive web interface

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

### Port Already in Use
If port 8501 is already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Use different external port
```

## License

Apache License 2.0